from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from backend.database.postgresql import get_session
from backend.database.orm_models import EmployeeORM
from backend.models.employee import Employee, EmployeeUpdate

router = APIRouter(prefix="/api/employees", tags=["Employees"])


def _orm_to_dict(obj: EmployeeORM) -> dict:
    return {
        "employee_id": obj.employee_id,
        "name": obj.name,
        "skills": obj.skills,
        "experience_years": obj.experience_years,
        "certifications": obj.certifications,
        "domain": obj.domain,
        "availability": obj.availability,
        "availability_date": obj.availability_date,
        "utilization_percent": obj.utilization_percent,
        "bench_since": obj.bench_since,
        "resume_text": obj.resume_text,
    }


@router.get("/")
async def list_employees(
    availability: str = None,
    skill: str = None,
    session: AsyncSession = Depends(get_session),
):
    stmt = select(EmployeeORM)
    if availability:
        stmt = stmt.where(EmployeeORM.availability == availability)
    result = await session.execute(stmt)
    employees = result.scalars().all()
    if skill:
        employees = [e for e in employees if skill in (e.skills or [])]
    return [_orm_to_dict(e) for e in employees]


@router.get("/{employee_id}")
async def get_employee(employee_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(EmployeeORM).where(EmployeeORM.employee_id == employee_id)
    )
    emp = result.scalar_one_or_none()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return _orm_to_dict(emp)


@router.post("/", status_code=201)
async def create_employee(employee: Employee, session: AsyncSession = Depends(get_session)):
    existing = await session.execute(
        select(EmployeeORM).where(EmployeeORM.employee_id == employee.employee_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Employee ID already exists")
    new_emp = EmployeeORM(**employee.model_dump())
    session.add(new_emp)
    await session.commit()
    return {"message": "Employee created", "employee_id": employee.employee_id}


@router.put("/{employee_id}")
async def update_employee(
    employee_id: str,
    update_data: EmployeeUpdate,
    session: AsyncSession = Depends(get_session),
):
    fields = {k: v for k, v in update_data.model_dump().items() if v is not None}
    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    result = await session.execute(
        update(EmployeeORM).where(EmployeeORM.employee_id == employee_id).values(**fields)
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Employee not found")
    await session.commit()
    return {"message": "Employee updated"}


@router.delete("/{employee_id}")
async def delete_employee(employee_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        delete(EmployeeORM).where(EmployeeORM.employee_id == employee_id)
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Employee not found")
    await session.commit()
    return {"message": "Employee deleted"}
