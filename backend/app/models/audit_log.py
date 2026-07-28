"""
Audit log database model.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func

from app.database import Base


class AuditLog(Base):
    """Represents a system audit event."""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(100), nullable=False, index=True)
    entity_type = Column(String(100), nullable=True, index=True)
    entity_id = Column(String(100), nullable=True, index=True)
    details = Column(Text, nullable=True)
    actor = Column(String(150), nullable=True, index=True)
    actor_role = Column(String(50), nullable=True, index=True)
    source = Column(String(100), nullable=True, index=True)
    created_at = Column(DateTime, server_default=func.now())
