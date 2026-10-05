from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def create_audit_log(
    db: Session,
    user_id: int,
    action: str,
    table_name: str,
    record_id: int,
    old_values: dict | None = None,
    new_values: dict | None = None
):
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        table_name=table_name,
        record_id=record_id,
        old_values=old_values,
        new_values=new_values
    )

    db.add(audit_log)
    db.flush()   
    return audit_log