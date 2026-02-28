# app/Schemas/client.py

from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, ConfigDict
from uuid import UUID

class ClientBase(BaseModel):
    name: str
    code: str

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None

class ClientRead(ClientBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)
