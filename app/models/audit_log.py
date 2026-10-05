from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True
    )

    action: Mapped[str] = mapped_column(
        String(20)
    )

    table_name: Mapped[str] = mapped_column(
        String(50)
    )

    record_id: Mapped[int]

    old_values: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True
    )

    new_values: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(ZoneInfo("Asia/Kolkata"))
    )