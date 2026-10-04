# Projeto Desenvolvido na Data Science Academy

"""Serviço de Pedidos — Camada de domínio responsável pela orquestração
das regras de negócio relacionadas à criação, consulta e atualização de pedidos.

Este serviço NÃO controla commit/rollback da transação.
A responsabilidade transacional fica na camada superior (router/controller),
permitindo composição de operações e maior controle de consistência.
"""

import logging
import random
import string
from uuid import uuid4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product
from app.schemas.order_schema import OrderCreate, OrderItemResponse, OrderResponse

logger = logging.getLogger(__name__)

# Define a máquina de estados do pedido.
# Garante integridade do fluxo de negócio, evitando transições inválidas.
# Estados finais não permitem novas mudanças.
VALID_TRANSITIONS: dict[OrderStatus, list[OrderStatus]] = {
    OrderStatus.CONFIRMED: [OrderStatus.PROCESSING, OrderStatus.CANCELLED],
    OrderStatus.PROCESSING: [OrderStatus.SHIPPED, OrderStatus.CANCELLED],
    OrderStatus.SHIPPED: [OrderStatus.DELIVERED],
    OrderStatus.DELIVERED: [],
    OrderStatus.CANCELLED: [],
}


class OrderService:
    """Serviço de domínio para pedidos.

    Atua como camada de orquestração entre:
    - Persistência (SQLAlchemy ORM)
    - Regras de negócio (estoque, status, total)
    - Contratos de saída (schemas)

    Depende de uma sessão assíncrona do SQLAlchemy (AsyncSession),
    que deve ser gerenciada externamente.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    def dsa__generate_tracking_code(self) -> str:
        """Gera um código de rastreamento fictício.

        Observação:
        - Não garante unicidade absoluta
        - Em sistemas reais, isso deveria ser delegado a um serviço externo
          ou possuir constraint no banco
        """
        suffix = "".join(random.choices(string.digits, k=9))

        return f"BR{suffix}XX"

    def dsa__generate_order_id(self) -> str:
        """Gera um ID de pedido.

        Usa UUID truncado para reduzir colisões mantendo legibilidade.
        Em cenários críticos, pode-se usar ULID ou UUID completo.
        """
        return f"ORD-{uuid4().hex[:8].upper()}"

    async def dsa_create_order(self, order_data: OrderCreate) -> OrderResponse:
        """Cria um pedido com validação de estoque e cálculo do total.

        Pontos críticos:
        - Controle de concorrência no estoque (race condition)
        - Consistência transacional
        - Cálculo determinístico do total

        Estratégia:
        - SELECT ... FOR UPDATE para lock pessimista (PostgreSQL)
        - Atualização do estoque dentro da mesma transação
        - flush() em vez de commit() para manter controle externo
        """
        total = 0.0
        items = []

        for item_data in order_data.items:

            # Construção da query base
            stmt = select(Product).where(Product.id == item_data.product_id)

            try:
                # Lock pessimista:
                # Bloqueia a linha do produto até o fim da transação,
                # evitando que outra transação leia/modifique simultaneamente.
                result = await self.db.execute(stmt.with_for_update())
            except Exception:
                # Fallback para bancos sem suporte (ex: SQLite)
                # Nesse caso, perde-se proteção contra concorrência real.
                result = await self.db.execute(stmt)

            product = result.scalar_one_or_none()

            if not product:
                raise ValueError(f"Produto {item_data.product_id} não encontrado")

            # Validação de regra de negócio: estoque suficiente
            if product.stock < item_data.quantity:
                raise ValueError(
                    f"Estoque insuficiente para {product.name}. "
                    f"Disponível: {product.stock}, Solicitado: {item_data.quantity}"
                )

            # Cálculo do valor do item
            item_total = float(product.price) * item_data.quantity
            total += item_total

            # Criação do item do pedido (ainda em memória)
            item = OrderItem(
                id=f"{order_data.customer_id}-{item_data.product_id}-{uuid4().hex[:6]}",
                product_id=item_data.product_id,
                quantity=item_data.quantity,
                unit_price=float(product.price),
            )
            items.append(item)

            # Atualização do estoque em memória 
            # Será persistido no flush/commit
            product.stock -= item_data.quantity

        # Criação do pedido principal
        order_id = self.dsa__generate_order_id()
        order = Order(
            id=order_id,
            customer_id=order_data.customer_id,
            status=OrderStatus.CONFIRMED.value,
            total=total,
            tracking_code=self.dsa__generate_tracking_code(),
        )

        # Associação dos itens ao pedido
        for item in items:
            item.order_id = order_id

        # Registro no contexto da sessão (ainda não persistido no banco)
        self.db.add(order)
        for item in items:
            self.db.add(item)

        # flush:
        # - Executa INSERTs/UPDATEs no banco
        # - Mantém a transação aberta
        # - Permite rollback posterior caso necessário
        await self.db.flush()

        # Recarrega o pedido do banco para garantir:
        # - Relacionamentos carregados corretamente
        # - Estado consistente com o banco
        result = await self.db.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one()

        return self.dsa__to_response(order)

    async def dsa_get_order(self, order_id: str) -> OrderResponse | None:
        """Busca um pedido por ID.

        Retorna None se não encontrado.
        Não levanta exceção para facilitar uso em APIs REST.
        """
        result = await self.db.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one_or_none()

        if not order:
            return None

        return self.dsa__to_response(order)

    async def dsa_get_by_tracking_code(self, tracking_code: str) -> OrderResponse | None:
        """Busca pedido por código de rastreamento.

        Geralmente usado por clientes finais (tracking público).
        """
        result = await self.db.execute(select(Order).where(Order.tracking_code == tracking_code))
        order = result.scalar_one_or_none()

        if not order:
            return None

        return self.dsa__to_response(order)

    async def dsa_get_customer_orders(self, customer_id: str, page: int = 1, per_page: int = 20) -> tuple[list[OrderResponse], int]:
        """Lista pedidos de um cliente com paginação.

        Retorna:
        - Lista de pedidos
        - Total de registros (para paginação no frontend)
        """
        from sqlalchemy import func

        # Query de contagem total (para paginação)
        count_result = await self.db.execute(select(func.count(Order.id)).where(Order.customer_id == customer_id))
        total = count_result.scalar() or 0

        # Cálculo de offset baseado na página
        offset = (page - 1) * per_page

        # Query paginada e ordenada por data
        result = await self.db.execute(
            select(Order)
            .where(Order.customer_id == customer_id)
            .order_by(Order.created_at.desc())
            .offset(offset)
            .limit(per_page)
        )

        orders = list(result.scalars().all())

        return [self.dsa__to_response(o) for o in orders], total

    async def dsa_update_status(self, order_id: str, new_status: OrderStatus) -> OrderResponse | None:
        """Atualiza o status do pedido.

        Aplica validação baseada na máquina de estados,
        garantindo integridade do fluxo de negócio.
        """
        result = await self.db.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one_or_none()

        if not order:
            return None

        current_status = OrderStatus(order.status)
        valid_next = VALID_TRANSITIONS.get(current_status, [])

        # Validação de transição
        if new_status not in valid_next:
            raise ValueError(
                f"Transição inválida: {order.status} -> {new_status.value}. "
                f"Transições válidas: {[s.value for s in valid_next]}"
            )

        # Atualização do estado
        order.status = new_status.value

        # flush para persistir alteração sem finalizar transação
        await self.db.flush()

        # refresh garante sincronização com o estado do banco
        await self.db.refresh(order)

        return self.dsa__to_response(order)

    def dsa__to_response(self, order: Order) -> OrderResponse:
        """Mapeia entidade ORM para schema de resposta.

        Função de transformação que desacopla:
        - Modelo de persistência (ORM)
        - Contrato de API (Pydantic)

        Evita vazamento de detalhes internos do banco.
        """
        items = []

        for item in order.items:
            # Acesso seguro ao relacionamento (lazy/eager loading)
            product_name = item.product.name if item.product else None

            items.append(
                OrderItemResponse(
                    id=item.id,
                    product_id=item.product_id,
                    product_name=product_name,
                    quantity=item.quantity,
                    unit_price=float(item.unit_price),
                )
            )

        return OrderResponse(
            id=order.id,
            customer_id=order.customer_id,
            status=order.status,
            total=float(order.total),
            tracking_code=order.tracking_code,
            items=items,
            created_at=order.created_at,
            updated_at=order.updated_at,
        )


        