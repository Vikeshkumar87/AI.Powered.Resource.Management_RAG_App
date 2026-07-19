from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from backend.database.postgresql import get_session
from backend.database.orm_models import ProjectORM
from backend.models.project import Project, ProjectUpdate

router = APIRouter(prefix="/api/projects", tags=["Projects"])


def _orm_to_dict(obj: ProjectORM) -> dict:
    return {
        "project_id": obj.project_id,
        "name": obj.name,
        "required_skills": obj.required_skills,
        "domain": obj.domain,
        "start_date": obj.start_date,
        "duration_months": obj.duration_months,
        "resources_needed": obj.resources_needed,
        "description": obj.description,
    }


@router.get("/")
async def list_projects(domain: str = None, session: AsyncSession = Depends(get_session)):
    stmt = select(ProjectORM)
    if domain:
        stmt = stmt.where(ProjectORM.domain == domain)
    result = await session.execute(stmt)
    return [_orm_to_dict(p) for p in result.scalars().all()]


@router.get("/{project_id}")
async def get_project(project_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(ProjectORM).where(ProjectORM.project_id == project_id)
    )
    proj = result.scalar_one_or_none()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    return _orm_to_dict(proj)


@router.post("/", status_code=201)
async def create_project(project: Project, session: AsyncSession = Depends(get_session)):
    existing = await session.execute(
        select(ProjectORM).where(ProjectORM.project_id == project.project_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Project ID already exists")
    session.add(ProjectORM(**project.model_dump()))
    await session.commit()
    return {"message": "Project created", "project_id": project.project_id}


@router.put("/{project_id}")
async def update_project(
    project_id: str,
    update_data: ProjectUpdate,
    session: AsyncSession = Depends(get_session),
):
    fields = {k: v for k, v in update_data.model_dump().items() if v is not None}
    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    result = await session.execute(
        update(ProjectORM).where(ProjectORM.project_id == project_id).values(**fields)
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    await session.commit()
    return {"message": "Project updated"}


@router.delete("/{project_id}")
async def delete_project(project_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        delete(ProjectORM).where(ProjectORM.project_id == project_id)
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    await session.commit()
    return {"message": "Project deleted"}
