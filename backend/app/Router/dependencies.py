# app/Router/dependencies.py
from __future__ import annotations

from typing import cast, List
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.Infrastructure.db_supabase import get_db
from app.Models.user_supabase import UserSupabase
from app.Router.supabase_auth import get_current_claims, require_roles
from app.Repositories.user_role_repository import UserRoleRepository


class CurrentUser:
    def __init__(
        self,
        id: UUID,
        email: str,
        roles: list[str],
        is_admin: bool,
    ):
        self.id = id
        self.email = email
        self.roles = roles
        self.is_admin = is_admin


async def get_current_user(
    claims: dict = Depends(get_current_claims),
    db: AsyncSession = Depends(get_db),
) -> CurrentUser:
    """
    Restituisce un oggetto CurrentUser contenente id, email, ruoli e un flag is_admin.
    """
    user_id_str = claims.get("sub")
    if not user_id_str:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token claim 'sub' mancante")

    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token claim 'sub' non è un UUID valido")

    repo = UserRoleRepository(db)
    user_roles_models = await repo.list_user_roles(user_id)
    roles = [role.name for role in user_roles_models]
    is_admin = "admin" in roles

    return CurrentUser(id=user_id, email=cast(str, claims.get("email")), roles=roles, is_admin=is_admin)
