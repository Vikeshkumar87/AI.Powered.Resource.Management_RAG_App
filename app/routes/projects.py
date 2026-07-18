"""
Project management API routes.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

from app.database import get_db
from app.models.project import Project, ProjectStatus
from app.services.vector_store import VectorStoreService

router = APIRouter(prefix="/projects", tags=["Projects"])


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    project_code: str = Field(..., min_length=2, max_length=50)
    client: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = None
    status: str = Field(default=ProjectStatus.PLANNING)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    required_skills: List[str] = Field(default=[])
    team_size_required: int = Field(default=1, ge=1)
    budget: Optional[float] = Field(None, ge=0)
    priority: str = Field(default="medium")
    domain: Optional[str] = None
    location: Optional[str] = None
    manager_name: Optional[str] = None
    manager_email: Optional[str] = None
    notes: Optional[str] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    client: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    required_skills: Optional[List[str]] = None
    team_size_required: Optional[int] = Field(None, ge=1)
    budget: Optional[float] = Field(None, ge=0)
    priority: Optional[str] = None
    domain: Optional[str] = None
    location: Optional[str] = None
    manager_name: Optional[str] = None
    manager_email: Optional[str] = None
    notes: Optional[str] = None


class AllocationInfo(BaseModel):
    id: int
    resource_id: int
    resource_name: str
    role: str
    allocation_percentage: float
    start_date: datetime
    end_date: Optional[datetime]
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class ProjectResponse(BaseModel):
    id: int
    name: str
    project_code: str
    client: str
    description: Optional[str]
    status: str
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    required_skills: List[str]
    team_size_required: int
    current_team_size: int
    budget: Optional[float]
    priority: str
    domain: Optional[str]
    location: Optional[str]
    manager_name: Optional[str]
    manager_email: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectListResponse(BaseModel):
    total: int
    projects: List[ProjectResponse]


def _get_vector_store() -> VectorStoreService:
    return VectorStoreService()


@router.get("/", response_model=ProjectListResponse)
def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    client: Optional[str] = None,
    priority: Optional[str] = None,
    domain: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List all projects with optional filters."""
    query = db.query(Project)

    if status:
        query = query.filter(Project.status == status)
    if client:
        query = query.filter(Project.client.ilike(f"%{client}%"))
    if priority:
        query = query.filter(Project.priority == priority)
    if domain:
        query = query.filter(Project.domain.ilike(f"%{domain}%"))

    total = query.count()
    projects = query.offset(skip).limit(limit).all()

    return ProjectListResponse(total=total, projects=projects)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    """Get a specific project by ID."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail=f"Project with id {project_id} not found")
    return project


@router.post("/", response_model=ProjectResponse, status_code=201)
def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    vs: VectorStoreService = Depends(_get_vector_store),
):
    """Create a new project."""
    existing = db.query(Project).filter(
        Project.project_code == project_data.project_code
    ).first()
    if existing:
        raise HTTPException(
            status_code=400, detail="Project with this project_code already exists"
        )

    project = Project(**project_data.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)

    try:
        vs.add_project(project)
    except Exception:
        pass

    return project


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),
    vs: VectorStoreService = Depends(_get_vector_store),
):
    """Update an existing project."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail=f"Project with id {project_id} not found")

    update_data = project_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)

    try:
        vs.update_project(project)
    except Exception:
        pass

    return project


@router.delete("/{project_id}", status_code=204)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    vs: VectorStoreService = Depends(_get_vector_store),
):
    """Delete a project."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail=f"Project with id {project_id} not found")

    db.delete(project)
    db.commit()

    try:
        vs.delete_project(project_id)
    except Exception:
        pass


@router.get("/{project_id}/team", response_model=List[AllocationInfo])
def get_project_team(project_id: int, db: Session = Depends(get_db)):
    """Get the current team members allocated to a project."""
    from app.models.allocation import Allocation
    from app.models.resource import Resource

    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail=f"Project with id {project_id} not found")

    allocations = (
        db.query(Allocation)
        .filter(Allocation.project_id == project_id, Allocation.is_active == True)
        .all()
    )

    result = []
    for alloc in allocations:
        resource = db.query(Resource).filter(Resource.id == alloc.resource_id).first()
        result.append(
            AllocationInfo(
                id=alloc.id,
                resource_id=alloc.resource_id,
                resource_name=resource.name if resource else "Unknown",
                role=alloc.role,
                allocation_percentage=alloc.allocation_percentage,
                start_date=alloc.start_date,
                end_date=alloc.end_date,
                is_active=alloc.is_active,
            )
        )

    return result
