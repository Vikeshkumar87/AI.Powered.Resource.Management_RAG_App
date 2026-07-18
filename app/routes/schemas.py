"""
Pydantic schemas for Resource endpoints.
"""
from pydantic import BaseModel, EmailStr, Field
from pydantic import ConfigDict
from typing import List, Optional
from datetime import datetime


class ResourceBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Full name of the resource")
    email: str = Field(..., description="Email address")
    employee_id: str = Field(..., min_length=2, max_length=50, description="Employee ID")
    department: str = Field(..., description="Department name")
    designation: str = Field(..., description="Job designation/title")
    skills: List[str] = Field(default=[], description="List of skills")
    experience_years: float = Field(default=0.0, ge=0, le=60, description="Years of experience")
    location: Optional[str] = Field(None, description="Work location")
    availability_percentage: float = Field(default=100.0, ge=0, le=100, description="Availability %")
    is_on_bench: bool = Field(default=True, description="Whether resource is on bench")
    bench_start_date: Optional[datetime] = None
    expected_allocation_date: Optional[datetime] = None
    bio: Optional[str] = Field(None, description="Brief biography")
    certifications: List[str] = Field(default=[], description="List of certifications")
    preferred_roles: List[str] = Field(default=[], description="Preferred project roles")
    hourly_rate: Optional[float] = Field(None, ge=0, description="Hourly billing rate")


class ResourceCreate(ResourceBase):
    pass


class ResourceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    skills: Optional[List[str]] = None
    experience_years: Optional[float] = Field(None, ge=0, le=60)
    location: Optional[str] = None
    availability_percentage: Optional[float] = Field(None, ge=0, le=100)
    is_on_bench: Optional[bool] = None
    bench_start_date: Optional[datetime] = None
    expected_allocation_date: Optional[datetime] = None
    bio: Optional[str] = None
    certifications: Optional[List[str]] = None
    preferred_roles: Optional[List[str]] = None
    hourly_rate: Optional[float] = Field(None, ge=0)


class AllocationSummary(BaseModel):
    project_id: int
    project_name: Optional[str] = None
    role: str
    allocation_percentage: float
    start_date: datetime
    end_date: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class ResourceResponse(ResourceBase):
    id: int
    created_at: datetime
    updated_at: datetime
    allocations: List[AllocationSummary] = []

    model_config = ConfigDict(from_attributes=True)


class ResourceListResponse(BaseModel):
    total: int
    resources: List[ResourceResponse]
