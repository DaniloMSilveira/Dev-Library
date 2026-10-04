# Projeto Desenvolvido na Data Science Academy

"""Schemas Pydantic para Cliente."""

from datetime import datetime
from pydantic import BaseModel, EmailStr


class CustomerCreate(BaseModel):
    """Schema para criação de cliente."""

    name: str
    email: EmailStr


class CustomerResponse(BaseModel):
    """Schema de resposta com dados do cliente."""

    id: str
    name: str
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}
