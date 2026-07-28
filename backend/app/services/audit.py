"""
Audit logging helpers.
"""
import json
from typing import Any, Optional

from app.models.audit_log import AuditLog


def log_audit_event(
    action: str,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    details: Optional[dict[str, Any]] = None,
    actor: Optional[str] = None,
    actor_role: Optional[str] = None,
    source: Optional[str] = None,
    db=None,
) -> None:
    """Persist a simple audit event without interrupting the main request flow."""
    created_session = False
    if db is None:
        from app.database import SessionLocal

        db = SessionLocal()
        created_session = True
    try:
        db.add(
            AuditLog(
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                details=json.dumps(details or {}, ensure_ascii=True),
                actor=actor,
                actor_role=actor_role,
                source=source,
            )
        )
        db.commit()
    except Exception:
        db.rollback()
    finally:
        if created_session:
            db.close()
