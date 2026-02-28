"""Add orders polygons and holes tables

Revision ID: b6b7c8d9e0f1
Revises: a570362b739e
Create Date: 2026-02-28 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b6b7c8d9e0f1'
down_revision: Union[str, Sequence[str], None] = 'a570362b739e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Tabella orders
    op.create_table(
        'orders',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('code', sa.String(length=64), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['auth.users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='public'
    )
    op.create_index(op.f('ix_public_orders_code'), 'orders', ['code'], unique=True, schema='public')

    # Tabella polygons
    op.create_table(
        'polygons',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('order_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('label', sa.String(length=128), nullable=True),
        sa.Column('width_mm', sa.Float(), nullable=False),
        sa.Column('height_mm', sa.Float(), nullable=False),
        sa.Column('dxf_path', sa.String(length=255), nullable=True),
        sa.Column('preview_path', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['order_id'], ['public.orders.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='public'
    )

    # Tabella holes
    op.create_table(
        'holes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('polygon_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('type', sa.String(length=64), nullable=True),
        sa.Column('x_mm', sa.Float(), nullable=False),
        sa.Column('y_mm', sa.Float(), nullable=False),
        sa.Column('width_mm', sa.Float(), nullable=False),
        sa.Column('height_mm', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['polygon_id'], ['public.polygons.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='public'
    )


def downgrade() -> None:
    op.drop_table('holes', schema='public')
    op.drop_table('polygons', schema='public')
    op.drop_index(op.f('ix_public_orders_code'), table_name='orders', schema='public')
    op.drop_table('orders', schema='public')
