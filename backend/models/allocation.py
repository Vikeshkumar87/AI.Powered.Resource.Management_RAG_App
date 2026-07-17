from typing import Optional
from pydantic import BaseModel


class Allocation(BaseModel):
    allocation_id: str
    employee_id: str
    project_id: str
    start_date: str
    end_date: str
    performance_rating: float
    role: str


class AllocationUpdate(BaseModel):
    end_date: Optional[str] = None
    performance_rating: Optional[float] = None
    role: Optional[str] = None
