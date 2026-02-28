# app/Schemas/order.py

from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime

class HoleBase(BaseModel):
    type: Optional[str] = None
    x_mm: float
    y_mm: float
    width_mm: Optional[float] = None
    height_mm: Optional[float] = None
    diameter_mm: Optional[float] = None
    depth_mm: Optional[float] = None
    hole_library_id: Optional[UUID] = None

class HoleRead(HoleBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)

class PolygonBase(BaseModel):
    label: Optional[str] = None
    width_mm: float
    height_mm: float
    dxf_path: Optional[str] = None
    preview_path: Optional[str] = None
    is_mirrored: bool = False
    is_machining: bool = False
    material: Optional[str] = None
    thickness_mm: Optional[float] = None

class PolygonRead(PolygonBase):
    id: UUID
    holes: List[HoleRead] = []
    model_config = ConfigDict(from_attributes=True)

class OrderBase(BaseModel):
    code: str
    client_id: Optional[UUID] = None

class OrderRead(OrderBase):
    id: UUID
    user_id: Optional[UUID] = None
    created_at: datetime
    polygons: List[PolygonRead] = []
    model_config = ConfigDict(from_attributes=True)
