# app/Models/polygon.py

from __future__ import annotations
from typing import TYPE_CHECKING, List
from sqlalchemy import String, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.Infrastructure.db_supabase import Base
from uuid import UUID
import uuid

if TYPE_CHECKING:
    from .order import Order
    from .hole import Hole

class Polygon(Base):
    __tablename__ = "polygons"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    order_id: Mapped[UUID] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"))
    label: Mapped[str] = mapped_column(String(128), nullable=True) # e.g. "X4 - START TIME"
    width_mm: Mapped[float] = mapped_column(Float)
    height_mm: Mapped[float] = mapped_column(Float)
    dxf_path: Mapped[str] = mapped_column(String(255), nullable=True)
    preview_path: Mapped[str] = mapped_column(String(255), nullable=True)
    is_mirrored: Mapped[bool] = mapped_column(default=False)
    is_machining: Mapped[bool] = mapped_column(default=False)
    material: Mapped[str] = mapped_column(String(128), nullable=True)
    thickness_mm: Mapped[float] = mapped_column(Float, nullable=True)

    order: Mapped[Order] = relationship(back_populates="polygons")
    holes: Mapped[List[Hole]] = relationship(back_populates="polygon", cascade="all, delete-orphan")
