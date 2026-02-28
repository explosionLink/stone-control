# app/Models/order.py

from __future__ import annotations
from typing import TYPE_CHECKING, List
from sqlalchemy import String, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.Infrastructure.db_supabase import Base
from uuid import UUID
import uuid

if TYPE_CHECKING:
    from .polygon import Polygon

class Order(Base):
    __tablename__ = "orders"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    polygons: Mapped[List[Polygon]] = relationship(back_populates="order", cascade="all, delete-orphan")
