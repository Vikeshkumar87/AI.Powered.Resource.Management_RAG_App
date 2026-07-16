"""
Allocation management API routes.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from app.database import get_db
from app.models.allocation import Allocation
from app.models.resource import Resource
from app.models.project import Project

router = APIRouter(prefix="/allocations", tags=["Allocations"])


class AllocationCreate(BaseModel):
    resource_id: int
    project_id: int
    role: str = Field(..., min_length=2, max_length=100)
    allocation_percentage: float = Field(default=100.0, ge=1, le=100)
    start_date: datetime
    end_date: Optional[datetime] = None
    notes: Optional[str] = None
    created_by: Optional[str] = None


class AllocationResponse(BaseModel):
    id: int
    resource_id: int
    resource_name: str
    project_id: int
    project_name: str
    role: str
    allocation_percentage: float
    start_date: datetime
    end_date: Optional[datetime]
    is_active: bool
    notes: Optional[str]
    created_by: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


def _enrich_allocation(alloc: Allocation, db: Session) -> AllocationResponse:
    """Enrich allocation with resource and project names."""
    resource = db.query(Resource).filter(Resource.id == alloc.resource_id).first()
    project = db.query(Project).filter(Project.id == alloc.project_id).first()
    return AllocationResponse(
        id=alloc.id,
        resource_id=alloc.resource_id,
        resource_name=resource.name if resource else "Unknown",
        project_id=alloc.project_id,
        project_name=project.name if project else "Unknown",
        role=alloc.role,
        allocation_percentage=alloc.allocation_percentage,
        start_date=alloc.start_date,
        end_date=alloc.end_date,
        is_active=alloc.is_active,
        notes=alloc.notes,
        created_by=alloc.created_by,
        created_at=alloc.created_at,
    )


@router.get("/", response_model=List[AllocationResponse])
def list_allocations(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    resource_id: Optional[int] = None,
    project_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    """List all allocations with optional filters."""
    query = db.query(Allocation)
    if resource_id is not None:
        query = query.filter(Allocation.resource_id == resource_id)
    if project_id is not None:
        query = query.filter(Allocation.project_id == project_id)
    if is_active is not None:
        query = query.filter(Allocation.is_active == is_active)

    allocations = query.offset(skip).limit(limit).all()
    return [_enrich_allocation(a, db) for a in allocations]


@router.post("/", response_model=AllocationResponse, status_code=201)
def create_allocation(
    data: AllocationCreate,
    db: Session = Depends(get_db),
):
    """Create a new resource allocation."""
    resource = db.query(Resource).filter(Resource.id == data.resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail=f"Resource {data.resource_id} not found")

    project = db.query(Project).filter(Project.id == data.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {data.project_id} not found")

    # Check total allocation does not exceed 100%
    existing_allocs = (
        db.query(Allocation)
        .filter(Allocation.resource_id == data.resource_id, Allocation.is_active == True)
        .all()
    )
    total_allocated = sum(a.allocation_percentage for a in existing_allocs)
    if total_allocated + data.allocation_percentage > 100.0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot allocate {data.allocation_percentage}% - resource only has "
                   f"{100 - total_allocated:.1f}% availability remaining",
        )

    allocation = Allocation(
        resource_id=data.resource_id,
        project_id=data.project_id,
        role=data.role,
        allocation_percentage=data.allocation_percentage,
        start_date=data.start_date,
        end_date=data.end_date,
        notes=data.notes,
        created_by=data.created_by,
        is_active=True,
    )
    db.add(allocation)

    # Update resource bench status
    resource.is_on_bench = False
    resource.availability_percentage = 100.0 - (total_allocated + data.allocation_percentage)
    resource.bench_start_date = None

    # Update project team size
    project.current_team_size = (
        db.query(Allocation)
        .filter(Allocation.project_id == data.project_id, Allocation.is_active == True)
        .count()
        + 1
    )

    db.commit()
    db.refresh(allocation)

    return _enrich_allocation(allocation, db)


@router.get("/{allocation_id}", response_model=AllocationResponse)
def get_allocation(allocation_id: int, db: Session = Depends(get_db)):
    """Get a specific allocation by ID."""
    allocation = db.query(Allocation).filter(Allocation.id == allocation_id).first()
    if not allocation:
        raise HTTPException(status_code=404, detail=f"Allocation {allocation_id} not found")
    return _enrich_allocation(allocation, db)


@router.delete("/{allocation_id}", status_code=204)
def delete_allocation(allocation_id: int, db: Session = Depends(get_db)):
    """End/delete an allocation and move resource to bench if no other active allocations."""
    allocation = db.query(Allocation).filter(Allocation.id == allocation_id).first()
    if not allocation:
        raise HTTPException(status_code=404, detail=f"Allocation {allocation_id} not found")

    resource = db.query(Resource).filter(Resource.id == allocation.resource_id).first()
    project = db.query(Project).filter(Project.id == allocation.project_id).first()

    allocation.is_active = False
    allocation.end_date = datetime.utcnow()

    if project and project.current_team_size > 0:
        project.current_team_size -= 1

    # Check if resource has any other active allocations
    other_allocs = (
        db.query(Allocation)
        .filter(
            Allocation.resource_id == allocation.resource_id,
            Allocation.is_active == True,
            Allocation.id != allocation_id,
        )
        .all()
    )

    if resource:
        if not other_allocs:
            resource.is_on_bench = True
            resource.availability_percentage = 100.0
            resource.bench_start_date = datetime.utcnow()
        else:
            total_allocated = sum(a.allocation_percentage for a in other_allocs)
            resource.availability_percentage = 100.0 - total_allocated

    db.commit()
