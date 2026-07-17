"""
Project database model.
"""
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class ProjectStatus(str, enum.Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Project(Base):
    """Represents a project that resources can be allocated to."""

    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    project_code = Column(String(50), unique=True, nullable=False)
    client = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), default=ProjectStatus.PLANNING)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    required_skills = Column(JSON, default=list)  # List of required skills
    team_size_required = Column(Integer, default=1)
    current_team_size = Column(Integer, default=0)
    budget = Column(Float, nullable=True)
    priority = Column(String(20), default="medium")  # low, medium, high, critical
    domain = Column(String(100), nullable=True)  # e.g., "FinTech", "Healthcare"
    location = Column(String(100), nullable=True)
    manager_name = Column(String(100), nullable=True)
    manager_email = Column(String(150), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    allocations = relationship("Allocation", back_populates="project")

    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}', client='{self.client}')>"

    def to_document_string(self) -> str:
        """Convert project to a string for vector embedding."""
        skills_str = ", ".join(self.required_skills) if self.required_skills else "Not specified"

        return (
            f"Project: {self.name} | Code: {self.project_code} | "
            f"Client: {self.client} | Status: {self.status} | "
            f"Domain: {self.domain or 'General'} | Priority: {self.priority} | "
            f"Required Skills: {skills_str} | "
            f"Team Size: {self.current_team_size}/{self.team_size_required} | "
            f"Location: {self.location or 'Remote'} | "
            f"Description: {self.description or 'No description'}"
        )
