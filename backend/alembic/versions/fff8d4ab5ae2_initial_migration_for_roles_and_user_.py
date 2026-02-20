"""Initial migration for roles and user_roles

Revision ID: fff8d4ab5ae2
Revises:
Create Date: 2026-02-20 16:02:53.814359

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'fff8d4ab5ae2'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Crea lo schema auth se non esiste (necessario per il riferimento della FK)
    op.execute('CREATE SCHEMA IF NOT EXISTS auth')

    # Tabella roles
    op.create_table(
        'roles',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=64), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        schema='public'
    )
    op.create_index(op.f('ix_public_roles_name'), 'roles', ['name'], unique=True, schema='public')

    # Tabella user_roles
    op.create_table(
        'user_roles',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['role_id'], ['public.roles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['auth.users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'role_id', name='uq_user_role'),
        schema='public'
    )
    op.create_index(op.f('ix_public_user_roles_role_id'), 'user_roles', ['role_id'], unique=False, schema='public')


def downgrade() -> None:
    op.drop_index(op.f('ix_public_user_roles_role_id'), table_name='user_roles', schema='public')
    op.drop_table('user_roles', schema='public')
    op.drop_index(op.f('ix_public_roles_name'), table_name='roles', schema='public')
    op.drop_table('roles', schema='public')
