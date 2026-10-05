"""add soft delete to order items

Revision ID: 887bc5a7ccb7
Revises: 47e7d129eb4a
Create Date: 2026-09-25 16:14:05.304995

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '887bc5a7ccb7'
down_revision: Union[str, Sequence[str], None] = '47e7d129eb4a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'order_items',
        sa.Column(
            'is_deleted',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('false')
        )
    )


def downgrade() -> None:
    op.drop_column('order_items', 'is_deleted')