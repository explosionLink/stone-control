# app/Repositories/user_supabase_repository.py

from __future__ import annotations

from typing import Optional, Sequence
from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.Models.user_supabase import UserSupabase

__all__ = ["UserSupabaseRepository"]  # <-- espone esplicitamente il simbolo


class UserSupabaseRepository:
    """
    Repository per interrogare/modificare la tabella `auth.users` (mappata dal modello `UserSupabase`).
    NOTA: per campi “sensibili” gestiti da Supabase Auth (es. email/password/phone/ban/meta),
    in produzione è preferibile usare le Admin API (service) e non scrivere direttamente sul DB.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # -------------------------
    # READ
    # -------------------------
    async def get(self, user_id: UUID) -> Optional[UserSupabase]:
        """
        Ritorna un utente per id (UUID) oppure None.
        """
        stmt = (
            select(UserSupabase)
            .where(UserSupabase.id == user_id)
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def list(self, offset: int = 0, limit: int = 50) -> Sequence[UserSupabase]:
        """
        Ritorna un elenco di utenti con paginazione.
        """
        stmt = select(UserSupabase).offset(offset).limit(limit)
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def get_by_email(self, email: str) -> Optional[UserSupabase]:
        """Ritorna un utente per email (se presente), altrimenti None."""
        stmt = select(UserSupabase).where(UserSupabase.email == email).limit(1)
        res = await self.db.execute(stmt)
        return res.scalars().first()

    # -------------------------
    # WRITE (pattern ORM robusto)
    # -------------------------
    async def update(self, user_id: UUID, data: dict) -> Optional[UserSupabase]:
        """
        Aggiorna i campi dell'utente con id dato e ritorna la riga aggiornata.
        ATTENZIONE: valuta l'uso del service Supabase Admin per i campi gestiti da Auth.
        """
        obj = await self.db.get(UserSupabase, user_id)
        if not obj:
            return None
        if data:
            for k, v in data.items():
                setattr(obj, k, v)
            await self.db.commit()
            await self.db.refresh(obj)
        return obj

    async def delete(self, user_id: UUID) -> bool:
        """
        Elimina l'utente con id dato.
        Ritorna True se almeno una riga è stata cancellata.
        """
        stmt = delete(UserSupabase).where(UserSupabase.id == user_id)
        res = await self.db.execute(stmt)
        await self.db.commit()
        return (res.rowcount or 0) > 0
