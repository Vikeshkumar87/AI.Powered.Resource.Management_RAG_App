from typing import List, Optional
from pydantic import BaseModel, Field


class Employee(BaseModel):
    employee_id: str
    name: str
    skills: List[str]
    experience_years: int
    certifications: List[str] = []
    domain: str
    availability: str  # "available" | "partial" | "allocated"
    availability_date: Optional[str] = None
    utilization_percent: int = 0
    bench_since: Optional[str] = None
    resume_text: str = ""


class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    skills: Optional[List[str]] = None
    experience_years: Optional[int] = None
    certifications: Optional[List[str]] = None
    domain: Optional[str] = None
    availability: Optional[str] = None
    availability_date: Optional[str] = None
    utilization_percent: Optional[int] = None
    bench_since: Optional[str] = None
    resume_text: Optional[str] = None
