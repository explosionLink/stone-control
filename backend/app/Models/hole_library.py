# app/Models/hole_library.py

from __future__ import annotations
from typing import TYPE_CHECKING, List
from sqlalchemy import String, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.Infrastructure.db_supabase import Base
from uuid import UUID
import uuid

if TYPE_CHECKING:
    from .hole import Hole

class HoleLibrary(Base):
    __tablename__ = "hole_library"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128))
    diameter_mm: Mapped[float] = mapped_column(Float, nullable=True)
    depth_mm: Mapped[float] = mapped_column(Float, nullable=True)

    holes: Mapped[List[Hole]] = relationship(back_populates="hole_definition")
