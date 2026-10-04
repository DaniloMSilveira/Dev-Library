# Projeto Desenvolvido na Data Science Academy

"""Router de Pedidos — Endpoints de criação, consulta e atualização de pedidos."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import dsa_get_db
from app.schemas.order_schema import OrderCreate, OrderResponse, OrderStatusUpdate
from app.services.order_service import OrderService

router = APIRouter(prefix="/api/v1/orders", tags=["Pedidos"])


@router.post("/", response_model=OrderResponse, status_code=201)
async def dsa_create_order(order_data: OrderCreate, db: AsyncSession = Depends(dsa_get_db)) -> OrderResponse:
    """Cria um novo pedido (checkout)."""
    service = OrderService(db)
    try:
        order = await service.dsa_create_order(order_data)
        await db.commit()
        return order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{order_id}", response_model=OrderResponse)
async def dsa_get_order(order_id: str, db: AsyncSession = Depends(dsa_get_db)) -> OrderResponse:
    """Retorna detalhes do pedido."""
    service = OrderService(db)
    order = await service.dsa_get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return order


@router.get("/tracking/{code}", response_model=OrderResponse)
async def dsa_get_by_tracking_code(code: str, db: AsyncSession = Depends(dsa_get_db)) -> OrderResponse:
    """Busca pedido por código de rastreamento."""
    service = OrderService(db)
    order = await service.dsa_get_by_tracking_code(code)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return order


@router.get("/customer/{customer_id}", response_model=dict)
async def dsa_get_customer_orders(
    customer_id: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(dsa_get_db),
) -> dict:
    """Retorna pedidos de um cliente com paginação."""
    service = OrderService(db)
    orders, total = await service.dsa_get_customer_orders(customer_id, page, per_page)
    return {"items": orders, "total": total, "page": page, "per_page": per_page}


@router.patch("/{order_id}/status", response_model=OrderResponse)
async def dsa_update_order_status(
    order_id: str,
    status_update: OrderStatusUpdate,
    db: AsyncSession = Depends(dsa_get_db),
) -> OrderResponse:
    """Atualiza o status de um pedido."""
    service = OrderService(db)
    try:
        order = await service.dsa_update_status(order_id, status_update.status)
        if not order:
            raise HTTPException(status_code=404, detail="Pedido não encontrado")
        await db.commit()
        return order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
