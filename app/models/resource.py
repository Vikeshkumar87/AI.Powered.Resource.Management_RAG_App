"""
Resource (Employee) database model.
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Resource(Base):
    """Represents an employee/resource in the organization."""

    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    email = Column(String(150), unique=True, nullable=False, index=True)
    employee_id = Column(String(50), unique=True, nullable=False)
    department = Column(String(100), nullable=False)
    designation = Column(String(100), nullable=False)
    skills = Column(JSON, nullable=False, default=list)  # List of skill strings
    experience_years = Column(Float, nullable=False, default=0.0)
    location = Column(String(100))
    availability_percentage = Column(Float, default=100.0)  # 0-100
    is_on_bench = Column(Boolean, default=True)
    bench_start_date = Column(DateTime, nullable=True)
    expected_allocation_date = Column(DateTime, nullable=True)
    bio = Column(Text, nullable=True)
    certifications = Column(JSON, default=list)  # List of certifications
    preferred_roles = Column(JSON, default=list)  # List of preferred roles
    hourly_rate = Column(Float, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    allocations = relationship("Allocation", back_populates="resource")

    def __repr__(self):
        return f"<Resource(id={self.id}, name='{self.name}', department='{self.department}')>"

    def to_document_string(self) -> str:
        """Convert resource to a string for vector embedding."""
        skills_str = ", ".join(self.skills) if self.skills else "No skills listed"
        certs_str = ", ".join(self.certifications) if self.certifications else "None"
        roles_str = ", ".join(self.preferred_roles) if self.preferred_roles else "Not specified"
        bench_status = "On Bench" if self.is_on_bench else "Allocated"

        return (
            f"Employee: {self.name} | ID: {self.employee_id} | "
            f"Department: {self.department} | Designation: {self.designation} | "
            f"Skills: {skills_str} | Experience: {self.experience_years} years | "
            f"Location: {self.location} | Availability: {self.availability_percentage}% | "
            f"Status: {bench_status} | Certifications: {certs_str} | "
            f"Preferred Roles: {roles_str} | "
            f"Bio: {self.bio or 'Not provided'}"
        )
