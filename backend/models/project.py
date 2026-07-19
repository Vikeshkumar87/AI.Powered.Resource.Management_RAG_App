from typing import List, Optional
from pydantic import BaseModel


class Project(BaseModel):
    project_id: str
    name: str
    required_skills: List[str]
    domain: str
    start_date: str
    duration_months: int
    resources_needed: int
    description: str = ""


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    required_skills: Optional[List[str]] = None
    domain: Optional[str] = None
    start_date: Optional[str] = None
    duration_months: Optional[int] = None
    resources_needed: Optional[int] = None
    description: Optional[str] = None
