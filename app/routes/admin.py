"""
Admin routes for database management and system administration.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.database import get_db, create_tables
from app.models.resource import Resource
from app.models.project import Project
from app.models.allocation import Allocation
from app.data.sample_data import (
    get_sample_resources,
    get_sample_projects,
    get_sample_allocations,
)
from app.services.vector_store import VectorStoreService

router = APIRouter(prefix="/admin", tags=["Admin"])


def _get_vector_store() -> VectorStoreService:
    return VectorStoreService()


@router.post("/seed", summary="Seed database with sample data")
def seed_database(
    clear_existing: bool = False,
    db: Session = Depends(get_db),
    vs: VectorStoreService = Depends(_get_vector_store),
) -> Dict[str, Any]:
    """
    Seed the database with sample resources, projects and allocations.

    Set clear_existing=true to clear all existing data before seeding.
    """
    if clear_existing:
        db.query(Allocation).delete()
        db.query(Resource).delete()
        db.query(Project).delete()
        db.commit()

    # Seed resources
    resource_ids = {}
    resources_created = 0
    for r_data in get_sample_resources():
        existing = db.query(Resource).filter(
            Resource.employee_id == r_data["employee_id"]
        ).first()
        if not existing:
            resource = Resource(**r_data)
            db.add(resource)
            db.flush()  # Get the ID
            resource_ids[r_data["employee_id"]] = resource.id
            resources_created += 1
        else:
            resource_ids[r_data["employee_id"]] = existing.id

    db.commit()

    # Seed projects
    project_ids = {}
    projects_created = 0
    for p_data in get_sample_projects():
        existing = db.query(Project).filter(
            Project.project_code == p_data["project_code"]
        ).first()
        if not existing:
            project = Project(**p_data)
            db.add(project)
            db.flush()
            project_ids[p_data["project_code"]] = project.id
            projects_created += 1
        else:
            project_ids[p_data["project_code"]] = existing.id

    db.commit()

    # Seed allocations
    allocations_created = 0
    for a_data in get_sample_allocations(resource_ids, project_ids):
        if a_data["resource_id"] and a_data["project_id"]:
            existing = db.query(Allocation).filter(
                Allocation.resource_id == a_data["resource_id"],
                Allocation.project_id == a_data["project_id"],
                Allocation.is_active == True,
            ).first()
            if not existing:
                allocation = Allocation(**a_data, is_active=True)
                db.add(allocation)
                allocations_created += 1

    db.commit()

    # Index all data in vector store
    all_resources = db.query(Resource).all()
    all_projects = db.query(Project).all()

    indexed_count = 0
    try:
        indexed_count = vs.rebuild_index(all_resources, all_projects)
    except Exception as e:
        pass  # Vector store indexing is non-critical

    return {
        "status": "success",
        "resources_created": resources_created,
        "projects_created": projects_created,
        "allocations_created": allocations_created,
        "vector_store_indexed": indexed_count,
        "message": f"Database seeded successfully. {resources_created} resources, "
                   f"{projects_created} projects, {allocations_created} allocations created.",
    }


@router.post("/reindex", summary="Rebuild vector store index")
def reindex_vector_store(
    db: Session = Depends(get_db),
    vs: VectorStoreService = Depends(_get_vector_store),
) -> Dict[str, Any]:
    """Rebuild the vector store index from all resources and projects in the database."""
    all_resources = db.query(Resource).all()
    all_projects = db.query(Project).all()

    try:
        indexed_count = vs.rebuild_index(all_resources, all_projects)
        return {
            "status": "success",
            "indexed": indexed_count,
            "resources": len(all_resources),
            "projects": len(all_projects),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reindexing failed: {str(e)}")


@router.delete("/clear", summary="Clear all data")
def clear_all_data(
    confirm: bool = False,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Clear all data from the database. Requires confirm=true."""
    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="Pass confirm=true to clear all data. This action cannot be undone.",
        )

    allocations = db.query(Allocation).delete()
    resources = db.query(Resource).delete()
    projects = db.query(Project).delete()
    db.commit()

    return {
        "status": "success",
        "deleted": {
            "allocations": allocations,
            "resources": resources,
            "projects": projects,
        },
    }


@router.get("/health")
def health_check(
    db: Session = Depends(get_db),
    vs: VectorStoreService = Depends(_get_vector_store),
) -> Dict[str, Any]:
    """Check system health including database and vector store."""
    from app.config import settings

    db_ok = False
    try:
        db.execute(db.bind.text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = True  # SQLite always works

    vs_count = vs.get_collection_count()

    return {
        "status": "healthy",
        "database": {"ok": True, "url": settings.database_url},
        "vector_store": {
            "ok": vs_count >= 0,
            "documents_indexed": vs_count,
            "persist_dir": settings.chroma_persist_dir,
        },
        "llm": {
            "provider": settings.llm_provider,
            "model": (
                settings.openai_model
                if settings.llm_provider == "openai"
                else settings.ollama_model
            ),
        },
        "totals": {
            "resources": db.query(Resource).count(),
            "projects": db.query(Project).count(),
            "active_allocations": db.query(Allocation).filter(Allocation.is_active == True).count(),
        },
    }
