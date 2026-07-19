from collections import Counter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from backend.database.postgresql import AsyncSessionLocal
from backend.database.orm_models import EmployeeORM, ProjectORM


async def get_dashboard_metrics() -> dict:
    async with AsyncSessionLocal() as session:
        # Total employees
        total = (await session.execute(select(func.count()).select_from(EmployeeORM))).scalar()

        # Available employees
        available = (
            await session.execute(
                select(func.count()).select_from(EmployeeORM).where(EmployeeORM.availability == "available")
            )
        ).scalar()

        bench_pct = round((available / total) * 100, 1) if total else 0.0

        # Average utilization
        avg_util = (
            await session.execute(select(func.avg(EmployeeORM.utilization_percent)))
        ).scalar()
        avg_utilization = round(float(avg_util or 0), 1)

        # Upcoming projects
        proj_result = await session.execute(select(ProjectORM))
        upcoming_projects = [
            {
                "name": p.name,
                "resources_needed": p.resources_needed,
                "start_date": p.start_date,
                "domain": p.domain,
            }
            for p in proj_result.scalars().all()
        ]

        # Bench employee list
        bench_result = await session.execute(
            select(EmployeeORM).where(EmployeeORM.availability == "available")
        )
        bench_employees = [
            {
                "employee_id": e.employee_id,
                "name": e.name,
                "skills": e.skills,
                "experience_years": e.experience_years,
                "bench_since": e.bench_since,
                "domain": e.domain,
            }
            for e in bench_result.scalars().all()
        ]

    return {
        "total_employees": total,
        "available_resources": available,
        "bench_percentage": bench_pct,
        "avg_utilization": avg_utilization,
        "upcoming_projects": upcoming_projects,
        "bench_employees": bench_employees,
    }


async def get_bench_by_skill() -> list:
    skill_count: Counter = Counter()
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(EmployeeORM).where(EmployeeORM.availability == "available")
        )
        for emp in result.scalars().all():
            for skill in emp.skills or []:
                skill_count[skill] += 1
    return [{"skill": s, "count": c} for s, c in skill_count.most_common(10)]


async def get_skill_demand() -> list:
    skill_count: Counter = Counter()
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(ProjectORM))
        for proj in result.scalars().all():
            for skill in proj.required_skills or []:
                skill_count[skill] += 1
    return [{"skill": s, "count": c} for s, c in skill_count.most_common(10)]
