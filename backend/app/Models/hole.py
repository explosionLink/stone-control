# app/Models/hole.py

from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.Infrastructure.db_supabase import Base
from uuid import UUID
import uuid

if TYPE_CHECKING:
    from .polygon import Polygon

class Hole(Base):
    __tablename__ = "holes"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    polygon_id: Mapped[UUID] = mapped_column(ForeignKey("polygons.id", ondelete="CASCADE"))
    type: Mapped[str] = mapped_column(String(64), nullable=True) # e.g. "lavello", "cottura"
    x_mm: Mapped[float] = mapped_column(Float)
    y_mm: Mapped[float] = mapped_column(Float)
    width_mm: Mapped[float] = mapped_column(Float, nullable=True)
    height_mm: Mapped[float] = mapped_column(Float, nullable=True)
    diameter_mm: Mapped[float] = mapped_column(Float, nullable=True)
    depth_mm: Mapped[float] = mapped_column(Float, nullable=True)
    hole_library_id: Mapped[UUID] = mapped_column(ForeignKey("hole_library.id"), nullable=True)

    polygon: Mapped[Polygon] = relationship(back_populates="holes")
    hole_definition: Mapped[HoleLibrary] = relationship(back_populates="holes")
