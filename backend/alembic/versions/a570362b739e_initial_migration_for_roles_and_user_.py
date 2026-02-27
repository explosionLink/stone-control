"""Initial migration for roles and user_roles

Revision ID: a570362b739e
Revises:
Create Date: 2026-02-20 16:15:00.000000

"""
from typing import Sequence, Union
import uuid
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a570362b739e'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Crea lo schema auth se non esiste
    op.execute('CREATE SCHEMA IF NOT EXISTS auth')
    # Abilita l'estensione pgcrypto per la gestione delle password
    op.execute('CREATE EXTENSION IF NOT EXISTS pgcrypto')

    # Tabella roles nel schema public
    op.create_table(
        'roles',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=64), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        schema='public'
    )
    op.create_index(op.f('ix_public_roles_name'), 'roles', ['name'], unique=True, schema='public')

    # Tabella user_roles nel schema public
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

    # Inserimento dati iniziali (Ruoli e Utente Admin)
    admin_role_id = 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'
    user_role_id = '0cc83a82-88f8-4ed9-9c92-ec9e09b266fd'
    admin_user_id = 'f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22'

    # 1. Inserimento dei ruoli
    op.execute(f"""
        INSERT INTO public.roles (id, name, description)
        VALUES
            ('{user_role_id}', 'user', 'Ruolo utente standard predefinito'),
            ('{admin_role_id}', 'admin', 'Ruolo amministratore con accesso completo')
        ON CONFLICT (id) DO NOTHING
    """)

    # 2. Inserimento dell'utente amministratore in auth.users
    # Usiamo pgcrypto per generare l'hash della password compatibile con Supabase
    op.execute(f"""
        INSERT INTO auth.users (
            instance_id, id, aud, role, email, encrypted_password,
            email_confirmed_at, recovery_sent_at, last_sign_in_at,
            raw_app_meta_data, raw_user_meta_data,
            created_at, updated_at, confirmation_token, email_change,
            email_change_token_new, recovery_token, phone, phone_confirmed_at
        )
        SELECT
            '00000000-0000-0000-0000-000000000000',
            '{admin_user_id}',
            'authenticated',
            'authenticated',
            'pietro.danieli.dev@gmail.com',
            crypt('explosionLink-117', gen_salt('bf')),
            now(), now(), now(),
            '{{"provider": "email", "providers": ["email"]}}',
            '{{"display_name": "Pietro Danieli"}}',
            now(), now(), '', '', '', '',
            '3921593130',
            now()
        WHERE NOT EXISTS (SELECT 1 FROM auth.users WHERE email = 'pietro.danieli.dev@gmail.com')
    """)

    # 3. Associazione ruolo admin
    op.execute(f"""
        INSERT INTO public.user_roles (id, user_id, role_id)
        SELECT gen_random_uuid(), id, '{admin_role_id}'
        FROM auth.users
        WHERE email = 'pietro.danieli.dev@gmail.com'
        ON CONFLICT (user_id, role_id) DO NOTHING
    """)


def downgrade() -> None:
    op.drop_index(op.f('ix_public_user_roles_role_id'), table_name='user_roles', schema='public')
    op.drop_table('user_roles', schema='public')
    op.drop_index(op.f('ix_public_roles_name'), table_name='roles', schema='public')
    op.drop_table('roles', schema='public')
