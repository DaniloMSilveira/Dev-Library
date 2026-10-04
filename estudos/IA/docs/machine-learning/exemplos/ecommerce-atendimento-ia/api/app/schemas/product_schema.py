# Projeto Desenvolvido na Data Science Academy

"""Schemas Pydantic para Produto."""

from datetime import datetime
from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    """Campos compartilhados de produto."""

    name: str
    description: str | None = None
    category: str
    brand: str
    price: float = Field(gt=0)
    stock: int = Field(ge=0)
    specs: dict | None = None
    image_url: str | None = None
    rating: float = Field(default=0, ge=0, le=5)
    reviews_count: int = Field(default=0, ge=0)


class ProductCreate(ProductBase):
    """Schema para criação de produto."""

    id: str


class ProductResponse(ProductBase):
    """Schema de resposta com dados completos do produto."""

    id: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ProductListResponse(BaseModel):
    """Schema de resposta paginada de produtos."""

    items: list[ProductResponse]
    total: int
    page: int
    per_page: int
