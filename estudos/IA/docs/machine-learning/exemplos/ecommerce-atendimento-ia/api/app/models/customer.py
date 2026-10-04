# Projeto Desenvolvido na Data Science Academy

"""Modelo Customer — Representa um cliente da loja."""

from datetime import datetime
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Customer(Base):
    """Modelo de cliente."""

    __tablename__ = "customers"

    id: Mapped[str] = mapped_column(String(20), primary_key = True)
    name: Mapped[str] = mapped_column(String(255), nullable = False)
    email: Mapped[str] = mapped_column(String(255), unique = True, nullable = False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    orders = relationship("Order", back_populates="customer", lazy="selectin", cascade="all, delete-orphan")
