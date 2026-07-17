"""
SQLAlchemy ORM table definitions for PostgreSQL.
JSON columns store lists (skills, certifications, required_skills).
"""
from sqlalchemy import Column, String, Integer, Float, JSON, Text
from backend.database.postgresql import Base  # shared DeclarativeBase


class EmployeeORM(Base):
    __tablename__ = "employees"

    employee_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    skills = Column(JSON, nullable=False, default=list)          # list[str]
    experience_years = Column(Integer, nullable=False)
    certifications = Column(JSON, nullable=False, default=list)  # list[str]
    domain = Column(String, nullable=False)
    availability = Column(String, nullable=False)                # available | partial | allocated
    availability_date = Column(String, nullable=True)
    utilization_percent = Column(Integer, default=0)
    bench_since = Column(String, nullable=True)
    resume_text = Column(Text, default="")


class ProjectORM(Base):
    __tablename__ = "projects"

    project_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    required_skills = Column(JSON, nullable=False, default=list)  # list[str]
    domain = Column(String, nullable=False)
    start_date = Column(String, nullable=False)
    duration_months = Column(Integer, nullable=False)
    resources_needed = Column(Integer, nullable=False)
    description = Column(Text, default="")


class AllocationORM(Base):
    __tablename__ = "allocations"

    allocation_id = Column(String, primary_key=True, index=True)
    employee_id = Column(String, nullable=False, index=True)
    project_id = Column(String, nullable=False, index=True)
    start_date = Column(String, nullable=False)
    end_date = Column(String, nullable=False)
    performance_rating = Column(Float, nullable=False)
    role = Column(String, nullable=False)
