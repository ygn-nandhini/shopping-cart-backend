"""rename total_amout to total_amount

Revision ID: b0d7a094fdb1
Revises: 72bc9a9772dd
Create Date: 2026-09-24 13:37:50.847778

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b0d7a094fdb1'
down_revision: Union[str, Sequence[str], None] = '72bc9a9772dd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('orders', 'total_amout', new_column_name='total_amount')


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('orders', 'total_amount', new_column_name='total_amout')