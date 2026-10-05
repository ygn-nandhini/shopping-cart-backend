from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.audit_log import AuditLog

router = APIRouter()
security = HTTPBearer()


@router.get(
    "/audit-logs",
    dependencies=[Depends(security)]
)
def get_audit_logs(
    db: Session = Depends(get_db)
):
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).all()
    return logs