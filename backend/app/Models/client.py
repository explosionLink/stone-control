# app/Models/client.py

from __future__ import annotations
from typing import TYPE_CHECKING, List
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.Infrastructure.db_supabase import Base
from uuid import UUID
import uuid

if TYPE_CHECKING:
    from .order import Order

class Client(Base):
    __tablename__ = "clients"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True) # e.g. "VENETA_CUCINE"

    orders: Mapped[List[Order]] = relationship(back_populates="client", cascade="all, delete-orphan")
