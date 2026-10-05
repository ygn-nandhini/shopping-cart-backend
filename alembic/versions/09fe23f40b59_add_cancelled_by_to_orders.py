"""add cancelled_by to orders

Revision ID: 09fe23f40b59
Revises: 9231fa49a9d4
Create Date: 2026-09-29 15:42:58.233766

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '09fe23f40b59'
down_revision: Union[str, Sequence[str], None] = '9231fa49a9d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('orders', sa.Column('cancelled_by', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'orders', 'users', ['cancelled_by'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('orders_cancelled_by_fkey', 'orders', type_='foreignkey')
    op.drop_column('orders', 'cancelled_by')