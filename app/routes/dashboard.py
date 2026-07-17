"""
Dashboard and analytics API routes.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, UTC

from app.database import get_db
from app.models.resource import Resource
from app.models.project import Project
from app.models.allocation import Allocation

router = APIRouter(prefix="/dashboard", tags=["Dashboard & Analytics"])


@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get high-level dashboard statistics."""
    total_resources = db.query(Resource).count()
    bench_resources = db.query(Resource).filter(Resource.is_on_bench == True).count()
    allocated_resources = total_resources - bench_resources

    total_projects = db.query(Project).count()
    active_projects = db.query(Project).filter(Project.status == "active").count()
    planning_projects = db.query(Project).filter(Project.status == "planning").count()

    total_allocations = db.query(Allocation).filter(Allocation.is_active == True).count()

    bench_percentage = (bench_resources / total_resources * 100) if total_resources > 0 else 0

    # Department breakdown
    dept_query = (
        db.query(Resource.department, func.count(Resource.id).label("count"))
        .group_by(Resource.department)
        .all()
    )
    departments = {dept: count for dept, count in dept_query}

    # Skills frequency
    all_resources = db.query(Resource).all()
    skill_counts: Dict[str, int] = {}
    for resource in all_resources:
        for skill in (resource.skills or []):
            skill_counts[skill] = skill_counts.get(skill, 0) + 1
    top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    return {
        "resources": {
            "total": total_resources,
            "on_bench": bench_resources,
            "allocated": allocated_resources,
            "bench_percentage": round(bench_percentage, 1),
        },
        "projects": {
            "total": total_projects,
            "active": active_projects,
            "planning": planning_projects,
            "completed": db.query(Project).filter(Project.status == "completed").count(),
        },
        "allocations": {
            "active": total_allocations,
        },
        "departments": departments,
        "top_skills": [{"skill": s, "count": c} for s, c in top_skills],
        "timestamp": datetime.now(UTC).isoformat(),
    }


@router.get("/bench-aging")
def get_bench_aging(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """Get bench resources sorted by how long they've been on bench."""
    bench_resources = (
        db.query(Resource)
        .filter(Resource.is_on_bench == True)
        .order_by(Resource.bench_start_date.asc().nullslast())
        .all()
    )

    now = datetime.now(UTC).replace(tzinfo=None)
    result = []
    for resource in bench_resources:
        days_on_bench = None
        if resource.bench_start_date:
            days_on_bench = (now - resource.bench_start_date).days

        result.append({
            "id": resource.id,
            "name": resource.name,
            "employee_id": resource.employee_id,
            "department": resource.department,
            "designation": resource.designation,
            "skills": resource.skills,
            "experience_years": resource.experience_years,
            "bench_start_date": resource.bench_start_date.isoformat() if resource.bench_start_date else None,
            "days_on_bench": days_on_bench,
            "expected_allocation_date": (
                resource.expected_allocation_date.isoformat()
                if resource.expected_allocation_date else None
            ),
            "aging_category": _categorize_bench_age(days_on_bench),
        })

    return result


def _categorize_bench_age(days: Optional[int]) -> str:
    """Categorize bench age into urgency levels."""
    if days is None:
        return "unknown"
    if days <= 14:
        return "fresh"       # 0-2 weeks: normal
    if days <= 30:
        return "moderate"    # 2-4 weeks: needs attention
    if days <= 60:
        return "aging"       # 1-2 months: urgent
    return "critical"        # >2 months: critical


@router.get("/project-gaps")
def get_project_gaps(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """Get projects that have unfilled resource requirements."""
    projects = db.query(Project).filter(
        Project.status.in_(["active", "planning"])
    ).all()

    gaps = []
    for project in projects:
        gap = project.team_size_required - project.current_team_size
        if gap > 0:
            gaps.append({
                "project_id": project.id,
                "project_name": project.name,
                "project_code": project.project_code,
                "client": project.client,
                "status": project.status,
                "priority": project.priority,
                "required_skills": project.required_skills,
                "team_size_required": project.team_size_required,
                "current_team_size": project.current_team_size,
                "gap": gap,
                "start_date": project.start_date.isoformat() if project.start_date else None,
            })

    # Sort by priority and gap size
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    gaps.sort(key=lambda x: (priority_order.get(x["priority"], 99), -x["gap"]))

    return gaps


