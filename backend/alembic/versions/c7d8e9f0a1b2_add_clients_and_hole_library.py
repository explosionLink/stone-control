"""Add clients and hole library

Revision ID: c7d8e9f0a1b2
Revises: b6b7c8d9e0f1
Create Date: 2026-03-01 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c7d8e9f0a1b2'
down_revision: Union[str, Sequence[str], None] = 'b6b7c8d9e0f1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Tabella clients
    op.create_table(
        'clients',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('code', sa.String(length=64), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        schema='public'
    )
    op.create_index(op.f('ix_public_clients_code'), 'clients', ['code'], unique=True, schema='public')
    op.create_index(op.f('ix_public_clients_name'), 'clients', ['name'], unique=True, schema='public')

    # Tabella hole_library
    op.create_table(
        'hole_library',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('code', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('diameter_mm', sa.Float(), nullable=True),
        sa.Column('depth_mm', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        schema='public'
    )
    op.create_index(op.f('ix_public_hole_library_code'), 'hole_library', ['code'], unique=True, schema='public')

    # Aggiornamento orders
    op.add_column('orders', sa.Column('client_id', postgresql.UUID(as_uuid=True), nullable=True), schema='public')
    op.create_foreign_key('fk_orders_clients', 'orders', 'clients', ['client_id'], ['id'], ondelete='CASCADE', source_schema='public', referent_schema='public')

    # Aggiornamento polygons
    op.add_column('polygons', sa.Column('is_mirrored', sa.Boolean(), server_default='false', nullable=False), schema='public')
    op.add_column('polygons', sa.Column('is_machining', sa.Boolean(), server_default='false', nullable=False), schema='public')
    op.add_column('polygons', sa.Column('material', sa.String(length=128), nullable=True), schema='public')
    op.add_column('polygons', sa.Column('thickness_mm', sa.Float(), nullable=True), schema='public')

    # Aggiornamento holes
    op.add_column('holes', sa.Column('diameter_mm', sa.Float(), nullable=True), schema='public')
    op.add_column('holes', sa.Column('depth_mm', sa.Float(), nullable=True), schema='public')
    op.add_column('holes', sa.Column('hole_library_id', postgresql.UUID(as_uuid=True), nullable=True), schema='public')
    op.create_foreign_key('fk_holes_hole_library', 'holes', 'hole_library', ['hole_library_id'], ['id'], source_schema='public', referent_schema='public')
    op.alter_column('holes', 'width_mm', existing_type=sa.Float(), nullable=True, schema='public')
    op.alter_column('holes', 'height_mm', existing_type=sa.Float(), nullable=True, schema='public')


def downgrade() -> None:
    op.drop_constraint('fk_holes_hole_library', 'holes', schema='public', type_='foreignkey')
    op.drop_column('holes', 'hole_library_id', schema='public')
    op.drop_column('holes', 'depth_mm', schema='public')
    op.drop_column('holes', 'diameter_mm', schema='public')
    op.alter_column('holes', 'height_mm', existing_type=sa.Float(), nullable=False, schema='public')
    op.alter_column('holes', 'width_mm', existing_type=sa.Float(), nullable=False, schema='public')

    op.drop_column('polygons', 'thickness_mm', schema='public')
    op.drop_column('polygons', 'material', schema='public')
    op.drop_column('polygons', 'is_machining', schema='public')
    op.drop_column('polygons', 'is_mirrored', schema='public')

    op.drop_constraint('fk_orders_clients', 'orders', schema='public', type_='foreignkey')
    op.drop_column('orders', 'client_id', schema='public')

    op.drop_index(op.f('ix_public_hole_library_code'), table_name='hole_library', schema='public')
    op.drop_table('hole_library', schema='public')
    op.drop_index(op.f('ix_public_clients_name'), table_name='clients', schema='public')
    op.drop_index(op.f('ix_public_clients_code'), table_name='clients', schema='public')
    op.drop_table('clients', schema='public')
