"""create audit logs table

Revision ID: b4fcbc033d01
Revises: c1c9f0b3c417
Create Date: 2026-09-25 23:14:51.010976
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b4fcbc033d01"
down_revision: Union[str, Sequence[str], None] = "c1c9f0b3c417"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create audit_logs table."""

    op.create_table(
        "audit_logs",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            nullable=False
        ),

        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id"),
            nullable=False
        ),

        sa.Column(
            "action",
            sa.String(length=20),
            nullable=False
        ),

        sa.Column(
            "table_name",
            sa.String(length=50),
            nullable=False
        ),

        sa.Column(
            "record_id",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False
        )
    )


def downgrade() -> None:
    """Drop audit_logs table."""

    op.drop_table("audit_logs")