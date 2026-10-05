"""add created_by to cart

Revision ID: 68cd4bca1985
Revises: 0cd82b4d83b6
Create Date: 2026-09-29 16:48:12.649291

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '68cd4bca1985'
down_revision: Union[str, Sequence[str], None] = '0cd82b4d83b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('cart', sa.Column('created_by', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'cart', 'users', ['created_by'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('cart_created_by_fkey', 'cart', type_='foreignkey')
    op.drop_column('cart', 'created_by')