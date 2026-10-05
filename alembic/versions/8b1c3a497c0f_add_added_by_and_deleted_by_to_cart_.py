"""add added_by and deleted_by to cart_items

Revision ID: 8b1c3a497c0f
Revises: 68cd4bca1985
Create Date: 2026-09-29 17:10:38.034236

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '8b1c3a497c0f'
down_revision: Union[str, Sequence[str], None] = '68cd4bca1985'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('cart_items', sa.Column('added_by', sa.Integer(), nullable=True))
    op.add_column('cart_items', sa.Column('deleted_by', sa.Integer(), nullable=True))
    op.create_foreign_key('cart_items_added_by_fkey', 'cart_items', 'users', ['added_by'], ['id'])
    op.create_foreign_key('cart_items_deleted_by_fkey', 'cart_items', 'users', ['deleted_by'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('cart_items_deleted_by_fkey', 'cart_items', type_='foreignkey')
    op.drop_constraint('cart_items_added_by_fkey', 'cart_items', type_='foreignkey')
    op.drop_column('cart_items', 'deleted_by')
    op.drop_column('cart_items', 'added_by')