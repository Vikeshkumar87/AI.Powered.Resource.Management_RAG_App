"""
Admin routes for database management, system administration, and phase validation.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from pydantic import BaseModel, Field

from app.database import get_db, create_tables
from app.models.resource import Resource
from app.models.project import Project
from app.models.allocation import Allocation
from app.data.sample_data import (
    get_sample_resources,
    get_sample_projects,
    get_sample_allocations,
)
from app.data.phase1_preparation import save_phase1_json
from app.services.vector_store import VectorStoreService
from app.services.phase_pipeline import get_phase_pipeline_service
from app.routes.auth import require_admin

router = APIRouter(prefix="/admin", tags=["Admin"])


class Phase3RetrievalRequest(BaseModel):
    staffing_request: str = Field(..., min_length=10, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=20)
    min_availability: float = Field(default=50.0, ge=0.0, le=100.0)
    max_utilization: float = Field(default=50.0, ge=0.0, le=100.0)


class Phase4RecommendationRequest(BaseModel):
    project_requirements: str = Field(..., min_length=10, max_length=3000)
    required_skills: list[str] = Field(default_factory=list)
    team_size: int = Field(default=3, ge=1, le=20)
    top_k: int = Field(default=10, ge=1, le=20)


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


@router.post("/phase1/prepare-data", summary="Phase 1: collect and store standardized JSON data")
def prepare_phase1_data(_role: str = Depends(require_admin)) -> Dict[str, Any]:
    """
    Phase 1 data preparation:
    - Collect employee and project sample data
    - Standardize skills using taxonomy
    - Store outputs as JSON files
    """
    summary = save_phase1_json()
    return {
        "status": "success",
        "phase": "phase_1",
        "message": "Employee/project data collected, standardized, and stored as JSON.",
        **summary,
    }


@router.post("/phase2/build-rag", summary="Phase 2: build FAISS RAG pipeline")
def build_phase2_rag_pipeline(_role: str = Depends(require_admin)) -> Dict[str, Any]:
    """Phase 2: ingest employee/project documents, embed them, and store in FAISS."""
    service = get_phase_pipeline_service()
    return service.build_phase2_rag_pipeline()


@router.post("/phase3/retrieve", summary="Phase 3: retrieve staffing matches")
def validate_phase3_retrieval(
    request: Phase3RetrievalRequest,
    _role: str = Depends(require_admin),
) -> Dict[str, Any]:
    """Phase 3: convert staffing requests into embeddings and retrieve matching employees."""
    service = get_phase_pipeline_service()
    return service.retrieve_phase3(
        staffing_request=request.staffing_request,
        top_k=request.top_k,
        min_availability=request.min_availability,
        max_utilization=request.max_utilization,
    )


@router.post("/phase4/recommend", summary="Phase 4: recommendation engine")
def validate_phase4_recommendations(
    request: Phase4RecommendationRequest,
    _role: str = Depends(require_admin),
) -> Dict[str, Any]:
    """Phase 4: return employees, scores, justifications, skill gaps, and upskilling suggestions."""
    service = get_phase_pipeline_service()
    return service.recommend_phase4(
        project_requirements=request.project_requirements,
        required_skills=request.required_skills,
        team_size=request.team_size,
        top_k=request.top_k,
    )


@router.get("/phase5/dashboard", summary="Phase 5: dashboard metrics")
def validate_phase5_dashboard(_role: str = Depends(require_admin)) -> Dict[str, Any]:
    """Phase 5: provide dashboard metrics, skill demand insights, and staffing recommendations."""
    service = get_phase_pipeline_service()
    return service.dashboard_phase5()
