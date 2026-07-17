"""
Resource management API routes.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models.resource import Resource
from app.models.allocation import Allocation
from app.models.project import Project
from app.routes.schemas import ResourceCreate, ResourceUpdate, ResourceResponse, ResourceListResponse
from app.services.vector_store import VectorStoreService

router = APIRouter(prefix="/resources", tags=["Resources"])


def _get_vector_store() -> VectorStoreService:
    return VectorStoreService()


@router.get("/", response_model=ResourceListResponse)
def list_resources(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    department: Optional[str] = None,
    is_on_bench: Optional[bool] = None,
    skill: Optional[str] = None,
    location: Optional[str] = None,
    min_experience: Optional[float] = Query(None, ge=0),
    db: Session = Depends(get_db),
):
    """List all resources with optional filters."""
    query = db.query(Resource)

    if department:
        query = query.filter(Resource.department.ilike(f"%{department}%"))
    if is_on_bench is not None:
        query = query.filter(Resource.is_on_bench == is_on_bench)
    if location:
        query = query.filter(Resource.location.ilike(f"%{location}%"))
    if min_experience is not None:
        query = query.filter(Resource.experience_years >= min_experience)
    if skill:
        # JSON contains filter - works for SQLite
        query = query.filter(Resource.skills.contains(skill))

    total = query.count()
    resources = query.offset(skip).limit(limit).all()

    return ResourceListResponse(total=total, resources=resources)


@router.get("/bench", response_model=ResourceListResponse)
def get_bench_resources(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    department: Optional[str] = None,
    skill: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Get all resources currently on bench (unallocated)."""
    query = db.query(Resource).filter(Resource.is_on_bench == True)

    if department:
        query = query.filter(Resource.department.ilike(f"%{department}%"))
    if skill:
        query = query.filter(Resource.skills.contains(skill))

    total = query.count()
    resources = query.offset(skip).limit(limit).all()

    return ResourceListResponse(total=total, resources=resources)


@router.get("/{resource_id}", response_model=ResourceResponse)
def get_resource(resource_id: int, db: Session = Depends(get_db)):
    """Get a specific resource by ID."""
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail=f"Resource with id {resource_id} not found")
    return resource


@router.post("/", response_model=ResourceResponse, status_code=201)
def create_resource(
    resource_data: ResourceCreate,
    db: Session = Depends(get_db),
    vs: VectorStoreService = Depends(_get_vector_store),
):
    """Create a new resource/employee."""
    # Check if email already exists
    existing = db.query(Resource).filter(Resource.email == resource_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Resource with this email already exists")

    # Check if employee_id already exists
    existing_id = db.query(Resource).filter(
        Resource.employee_id == resource_data.employee_id
    ).first()
    if existing_id:
        raise HTTPException(status_code=400, detail="Resource with this employee_id already exists")

    resource = Resource(**resource_data.model_dump())
    db.add(resource)
    db.commit()
    db.refresh(resource)

    # Add to vector store
    try:
        vs.add_resource(resource)
    except Exception:
        pass  # Non-critical: vector store update failure shouldn't block creation

    return resource


@router.put("/{resource_id}", response_model=ResourceResponse)
def update_resource(
    resource_id: int,
    resource_data: ResourceUpdate,
    db: Session = Depends(get_db),
    vs: VectorStoreService = Depends(_get_vector_store),
):
    """Update an existing resource."""
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail=f"Resource with id {resource_id} not found")

    update_data = resource_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(resource, field, value)

    db.commit()
    db.refresh(resource)

    # Update vector store
    try:
        vs.update_resource(resource)
    except Exception:
        pass

    return resource


@router.delete("/{resource_id}", status_code=204)
def delete_resource(
    resource_id: int,
    db: Session = Depends(get_db),
    vs: VectorStoreService = Depends(_get_vector_store),
):
    """Delete a resource."""
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail=f"Resource with id {resource_id} not found")

    db.delete(resource)
    db.commit()

    # Remove from vector store
    try:
        vs.delete_resource(resource_id)
    except Exception:
        pass


@router.post("/{resource_id}/allocate", response_model=ResourceResponse)
def allocate_resource(
    resource_id: int,
    project_id: int,
    role: str,
    start_date: datetime,
    end_date: Optional[datetime] = None,
    allocation_percentage: float = 100.0,
    db: Session = Depends(get_db),
):
    """Allocate a resource to a project."""
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail=f"Resource with id {resource_id} not found")

    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail=f"Project with id {project_id} not found")

    # Create allocation
    allocation = Allocation(
        resource_id=resource_id,
        project_id=project_id,
        role=role,
        allocation_percentage=allocation_percentage,
        start_date=start_date,
        end_date=end_date,
        is_active=True,
    )
    db.add(allocation)

    # Update resource bench status
    resource.is_on_bench = False
    resource.availability_percentage = 100.0 - allocation_percentage
    resource.bench_start_date = None

    # Update project team size
    project.current_team_size += 1

    db.commit()
    db.refresh(resource)
    return resource


@router.post("/{resource_id}/release", response_model=ResourceResponse)
def release_resource(
    resource_id: int,
    db: Session = Depends(get_db),
):
    """Release a resource from their current allocation (move to bench)."""
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail=f"Resource with id {resource_id} not found")

    # Deactivate all active allocations
    active_allocations = (
        db.query(Allocation)
        .filter(Allocation.resource_id == resource_id, Allocation.is_active == True)
        .all()
    )
    for alloc in active_allocations:
        alloc.is_active = False
        alloc.end_date = datetime.utcnow()
        # Update project team size
        project = db.query(Project).filter(Project.id == alloc.project_id).first()
        if project and project.current_team_size > 0:
            project.current_team_size -= 1

    # Move resource to bench
    resource.is_on_bench = True
    resource.availability_percentage = 100.0
    resource.bench_start_date = datetime.utcnow()

    db.commit()
    db.refresh(resource)
    return resource
