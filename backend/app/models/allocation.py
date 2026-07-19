"""
Allocation database model - tracks resource-to-project assignments.
"""
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Allocation(Base):
    """Represents the allocation of a resource to a project."""

    __tablename__ = "allocations"

    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    role = Column(String(100), nullable=False)  # Role in the project
    allocation_percentage = Column(Float, default=100.0)  # 0-100
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    resource = relationship("Resource", back_populates="allocations")
    project = relationship("Project", back_populates="allocations")

    def __repr__(self):
        return (
            f"<Allocation(id={self.id}, resource_id={self.resource_id}, "
            f"project_id={self.project_id}, role='{self.role}')>"
        )
