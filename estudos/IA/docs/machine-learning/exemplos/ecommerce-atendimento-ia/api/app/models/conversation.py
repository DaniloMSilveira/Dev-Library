# Projeto Desenvolvido na Data Science Academy

"""Modelo Conversation — Armazena histórico de conversas do chatbot."""

from datetime import datetime
from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Conversation(Base):
    """Modelo de conversa do chatbot."""

    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String(50), primary_key = True)
    
    customer_id: Mapped[str | None] = mapped_column(String(20), ForeignKey("customers.id"), nullable = True, index = True)
    
    messages: Mapped[list] = mapped_column(JSON, default = list)
    created_at: Mapped[datetime] = mapped_column(default = datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default = datetime.utcnow, onupdate = datetime.utcnow)
