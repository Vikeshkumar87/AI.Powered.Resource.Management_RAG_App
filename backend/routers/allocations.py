from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.database.postgresql import get_session
from backend.database.orm_models import AllocationORM
from backend.models.allocation import Allocation

router = APIRouter(prefix="/api/allocations", tags=["Allocations"])


def _orm_to_dict(obj: AllocationORM) -> dict:
    return {
        "allocation_id": obj.allocation_id,
        "employee_id": obj.employee_id,
        "project_id": obj.project_id,
        "start_date": obj.start_date,
        "end_date": obj.end_date,
        "performance_rating": obj.performance_rating,
        "role": obj.role,
    }


@router.get("/")
async def list_allocations(
    employee_id: str = None,
    project_id: str = None,
    session: AsyncSession = Depends(get_session),
):
    stmt = select(AllocationORM)
    if employee_id:
        stmt = stmt.where(AllocationORM.employee_id == employee_id)
    if project_id:
        stmt = stmt.where(AllocationORM.project_id == project_id)
    result = await session.execute(stmt)
    return [_orm_to_dict(a) for a in result.scalars().all()]


@router.get("/{allocation_id}")
async def get_allocation(allocation_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(AllocationORM).where(AllocationORM.allocation_id == allocation_id)
    )
    alloc = result.scalar_one_or_none()
    if not alloc:
        raise HTTPException(status_code=404, detail="Allocation not found")
    return _orm_to_dict(alloc)


@router.post("/", status_code=201)
async def create_allocation(allocation: Allocation, session: AsyncSession = Depends(get_session)):
    existing = await session.execute(
        select(AllocationORM).where(AllocationORM.allocation_id == allocation.allocation_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Allocation ID already exists")
    session.add(AllocationORM(**allocation.model_dump()))
    await session.commit()
    return {"message": "Allocation created", "allocation_id": allocation.allocation_id}
