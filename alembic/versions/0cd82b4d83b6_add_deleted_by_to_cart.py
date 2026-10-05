"""add deleted_by to cart

Revision ID: 0cd82b4d83b6
Revises: 09fe23f40b59
Create Date: 2026-09-29 16:39:42.481513

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0cd82b4d83b6'
down_revision: Union[str, Sequence[str], None] = '09fe23f40b59'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('cart', sa.Column('deleted_by', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'cart', 'users', ['deleted_by'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('cart_deleted_by_fkey', 'cart', type_='foreignkey')
    op.drop_column('cart', 'deleted_by')