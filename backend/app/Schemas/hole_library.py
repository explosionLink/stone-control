# app/Schemas/hole_library.py

from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, ConfigDict
from uuid import UUID

class HoleLibraryBase(BaseModel):
    code: str
    name: str
    diameter_mm: Optional[float] = None
    depth_mm: Optional[float] = None

class HoleLibraryCreate(HoleLibraryBase):
    pass

class HoleLibraryUpdate(BaseModel):
    name: Optional[str] = None
    diameter_mm: Optional[float] = None
    depth_mm: Optional[float] = None

class HoleLibraryRead(HoleLibraryBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)
