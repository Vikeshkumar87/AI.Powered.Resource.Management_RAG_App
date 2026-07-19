from fastapi import APIRouter
from backend.services.dashboard_service import get_dashboard_metrics, get_bench_by_skill, get_skill_demand

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/metrics")
async def dashboard_metrics():
    return await get_dashboard_metrics()


@router.get("/bench-by-skill")
async def bench_by_skill():
    return await get_bench_by_skill()


@router.get("/skill-demand")
async def skill_demand():
    return await get_skill_demand()
