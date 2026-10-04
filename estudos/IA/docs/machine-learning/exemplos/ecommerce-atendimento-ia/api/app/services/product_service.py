# Projeto Desenvolvido na Data Science Academy

"""Serviço de Produtos — Lógica de negócio para catálogo e estoque."""

import logging

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.types import Text as SAText
from app.models.product import Product
from app.schemas.product_schema import ProductListResponse, ProductResponse

logger = logging.getLogger(__name__)


class ProductService:
    """Serviço com lógica de negócio para produtos."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def dsa_list_products(
        self,
        category: str | None = None,
        brand: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        search: str | None = None,
        page: int = 1,
        per_page: int = 12,
    ) -> ProductListResponse:
        """Lista produtos com filtros e paginação."""
        query = select(Product)
        count_query = select(func.count(Product.id))

        if category:
            query = query.where(Product.category == category)
            count_query = count_query.where(Product.category == category)
        if brand:
            query = query.where(Product.brand == brand)
            count_query = count_query.where(Product.brand == brand)
        if min_price is not None:
            query = query.where(Product.price >= min_price)
            count_query = count_query.where(Product.price >= min_price)
        if max_price is not None:
            query = query.where(Product.price <= max_price)
            count_query = count_query.where(Product.price <= max_price)
        if search:
            search_filter = (
                Product.name.ilike(f"%{search}%")
                | Product.description.ilike(f"%{search}%")
                | Product.specs.cast(SAText).ilike(f"%{search}%")
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        total = (await self.db.execute(count_query)).scalar() or 0

        offset = (page - 1) * per_page
        query = query.offset(offset).limit(per_page).order_by(Product.name)
        result = await self.db.execute(query)
        products = list(result.scalars().all())

        return ProductListResponse(
            items=[ProductResponse.model_validate(p) for p in products],
            total=total,
            page=page,
            per_page=per_page,
        )

    async def dsa_get_product(self, product_id: str) -> Product | None:
        """Retorna um produto por ID."""
        result = await self.db.execute(select(Product).where(Product.id == product_id))
        
        return result.scalar_one_or_none()

    async def dsa_search_products(self, query: str) -> list[Product]:
        """Busca produtos por texto (nome, descrição e especificações).

        Busca pela query completa e também por cada termo individual,
        garantindo que buscas como '16 GB RAM' encontrem '16GB DDR5'.
        """
        terms = [query] + query.split()
        conditions = []
        for term in terms:
            term = term.strip()
            if not term:
                continue
            conditions.append(Product.name.ilike(f"%{term}%"))
            conditions.append(Product.description.ilike(f"%{term}%"))
            conditions.append(Product.specs.cast(SAText).ilike(f"%{term}%"))

        result = await self.db.execute(
            select(Product).where(or_(*conditions)).order_by(Product.rating.desc()).limit(20)
        )
        return list(result.scalars().all())

    async def dsa_get_categories(self) -> list[str]:
        """Lista categorias disponíveis."""
        result = await self.db.execute(select(Product.category).distinct().order_by(Product.category))
        return list(result.scalars().all())

    async def dsa_update_stock(self, product_id: str, quantity: int) -> bool:
        """Atualiza o estoque de um produto. Retorna True se bem-sucedido."""
        product = await self.dsa_get_product(product_id)
        if not product:
            return False
        product.stock = quantity
        # flush() em vez de commit() — o router controla o limite da transação
        await self.db.flush()
        return True
