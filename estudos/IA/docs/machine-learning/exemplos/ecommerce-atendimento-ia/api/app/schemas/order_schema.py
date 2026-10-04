# Projeto Desenvolvido na Data Science Academy
"""Schemas Pydantic para Pedido."""

from datetime import datetime
from pydantic import BaseModel, Field
from app.models.order import OrderStatus


class OrderItemCreate(BaseModel):
    """Schema para item de pedido na criação."""

    product_id: str
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    """Schema para criação de pedido."""

    customer_id: str
    items: list[OrderItemCreate] = Field(min_length=1)


class OrderItemResponse(BaseModel):
    """Schema de resposta de item de pedido."""

    id: str
    product_id: str
    product_name: str | None = None
    quantity: int
    unit_price: float

    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    """Schema de resposta com dados completos do pedido."""

    id: str
    customer_id: str
    status: str
    total: float
    tracking_code: str | None
    items: list[OrderItemResponse]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class OrderStatusUpdate(BaseModel):
    """Schema para atualização de status do pedido.

    A lógica de transição válida (ex: "confirmed" só pode ir para "processing")
    é validada na camada de serviço, não aqui.
    """

    status: OrderStatus
