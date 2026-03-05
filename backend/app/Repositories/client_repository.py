# app/Repositories/client_repository.py

from app.Core.base_repository import BaseRepository
from app.Models.client import Client
from app.Schemas.client import ClientCreate, ClientUpdate
from sqlalchemy.ext.asyncio import AsyncSession

class ClientRepository(BaseRepository[Client, ClientCreate, ClientUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(Client, session)
