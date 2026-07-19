"""
Phase 2-5 validation pipeline.

This module keeps the existing app behavior intact while adding a separate
phase-oriented workflow for:
- Phase 2: ingest documents, generate embeddings, store in FAISS
- Phase 3: retrieval with availability/utilization filtering
- Phase 4: recommendation engine outputs
- Phase 5: dashboard metrics and staffing insights
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

try:
    import faiss  # type: ignore
except ImportError:  # pragma: no cover - optional fallback only
    faiss = None

try:
    from app.config import settings
    from app.data.phase1_preparation import SKILL_TAXONOMY, prepare_phase1_data, save_phase1_json
except ModuleNotFoundError:  # pragma: no cover - package import fallback
    from backend.app.config import settings
    from backend.app.data.phase1_preparation import SKILL_TAXONOMY, prepare_phase1_data, save_phase1_json

from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


UPSKILL_GUIDANCE = {
    "backend": "Strengthen REST APIs, microservices, and database design through project-based practice.",
    "frontend": "Build UI components, state management patterns, and test coverage with React-focused projects.",
    "data_ai": "Practice model training, experimentation, and deployment workflows on sample ML problems.",
    "cloud_devops": "Work on cloud infrastructure, deployment automation, and Kubernetes/Terraform labs.",
    "mobile": "Complete mobile app feature builds with platform-specific UI and API integration.",
    "quality_security": "Join automation, security review, and test design exercises for production readiness.",
    "product_management": "Improve stakeholder management, roadmap planning, and delivery tracking with agile ceremonies.",
}


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _phase2_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "phase2_artifacts"


def _phase2_files() -> Dict[str, Path]:
    base = _phase2_dir()
    return {
        "index": base / "faiss.index",
        "documents": base / "documents.json",
        "manifest": base / "manifest.json",
        "embeddings": base / "embeddings.npy",
    }


def _load_phase1_payloads() -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    phase1_dir = Path(__file__).resolve().parents[1] / "data" / "phase1_json"
    employees_path = phase1_dir / "employees.json"
    projects_path = phase1_dir / "projects.json"

    if not employees_path.exists() or not projects_path.exists():
        save_phase1_json(phase1_dir)

    with employees_path.open("r", encoding="utf-8") as f:
        employees = json.load(f)
    with projects_path.open("r", encoding="utf-8") as f:
        projects = json.load(f)
    return employees, projects


def _resource_document(resource: Dict[str, Any]) -> str:
    skills = ", ".join(resource.get("skills", [])) or "No skills listed"
    certifications = ", ".join(resource.get("certifications", [])) or "None"
    roles = ", ".join(resource.get("preferred_roles", [])) or "Not specified"
    bench_status = "On Bench" if resource.get("is_on_bench") else "Allocated"
    availability = resource.get("availability_percentage", 0)
    return (
        f"Employee: {resource.get('name')} | ID: {resource.get('employee_id')} | "
        f"Department: {resource.get('department')} | Designation: {resource.get('designation')} | "
        f"Skills: {skills} | Experience: {resource.get('experience_years')} years | "
        f"Location: {resource.get('location')} | Availability: {availability}% | "
        f"Status: {bench_status} | Certifications: {certifications} | "
        f"Preferred Roles: {roles} | Bio: {resource.get('bio') or 'Not provided'}"
    )


def _project_document(project: Dict[str, Any]) -> str:
    skills = ", ".join(project.get("required_skills", [])) or "Not specified"
    return (
        f"Project: {project.get('name')} | Code: {project.get('project_code')} | "
        f"Client: {project.get('client')} | Status: {project.get('status')} | "
        f"Domain: {project.get('domain') or 'General'} | Priority: {project.get('priority')} | "
        f"Required Skills: {skills} | Team Size: {project.get('current_team_size')}/{project.get('team_size_required')} | "
        f"Location: {project.get('location') or 'Remote'} | Description: {project.get('description') or 'No description'}"
    )


def _skill_domain(skill: str) -> Optional[str]:
    lookup = skill.strip().lower()
    for domain, domain_skills in SKILL_TAXONOMY["domains"].items():
        if any(lookup == canonical.lower() for canonical in domain_skills):
            return domain
    return None


def _coverage_summary(required_skills: List[str], candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    covered = set()
    for candidate in candidates:
        covered.update(candidate.get("skills", []))

    gaps = [skill for skill in required_skills if skill not in covered]
    suggestions = []
    for gap in gaps:
        domain = _skill_domain(gap)
        suggestion = UPSKILL_GUIDANCE.get(domain, "Pair with mentoring and focused practice projects.")
        suggestions.append({"skill": gap, "domain": domain, "suggestion": suggestion})

    return {"skill_gaps": gaps, "upskilling_suggestions": suggestions}


class PhasePipelineService:
    """Phase 2-5 pipeline backed by FAISS and sentence embeddings."""

    def __init__(self):
        self._model = SentenceTransformer(settings.embedding_model)
        self._resources, self._projects = _load_phase1_payloads()
        self._artifacts = _phase2_dir()
        self._artifacts.mkdir(parents=True, exist_ok=True)
        self._documents: List[Dict[str, Any]] = []
        self._index = None
        self._embeddings: Optional[np.ndarray] = None

    @property
    def faiss_available(self) -> bool:
        return faiss is not None

    def _build_documents(self) -> List[Dict[str, Any]]:
        docs: List[Dict[str, Any]] = []
        for resource in self._resources:
            docs.append(
                {
                    "id": f"resource_{resource['employee_id']}",
                    "type": "resource",
                    "name": resource.get("name"),
                    "skills": resource.get("skills", []),
                    "availability_percentage": resource.get("availability_percentage", 0),
                    "utilization_percentage": round(100.0 - float(resource.get("availability_percentage", 0)), 1),
                    "is_on_bench": bool(resource.get("is_on_bench")),
                    "experience_years": resource.get("experience_years", 0),
                    "department": resource.get("department"),
                    "document": _resource_document(resource),
                    "source": "employee",
                }
            )

        for project in self._projects:
            docs.append(
                {
                    "id": f"project_{project['project_code']}",
                    "type": "project",
                    "name": project.get("name"),
                    "skills": project.get("required_skills", []),
                    "status": project.get("status"),
                    "team_size_required": project.get("team_size_required", 0),
                    "current_team_size": project.get("current_team_size", 0),
                    "gap": max(0, int(project.get("team_size_required", 0)) - int(project.get("current_team_size", 0))),
                    "priority": project.get("priority"),
                    "department": project.get("domain"),
                    "document": _project_document(project),
                    "source": "project",
                }
            )

        return docs

    def build_phase2_rag_pipeline(self) -> Dict[str, Any]:
        """Phase 2: ingest documents, embed, and store in FAISS."""
        self._documents = self._build_documents()
        texts = [doc["document"] for doc in self._documents]
        embeddings = self._model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
        embeddings = np.asarray(embeddings, dtype="float32")

        if faiss is not None:
            index = faiss.IndexFlatIP(embeddings.shape[1])
            index.add(embeddings)
            faiss.write_index(index, str(_phase2_files()["index"]))
            self._index = index

        self._embeddings = embeddings

        files = _phase2_files()
        with files["documents"].open("w", encoding="utf-8") as f:
            json.dump(self._documents, f, indent=2, ensure_ascii=True)
        with files["manifest"].open("w", encoding="utf-8") as f:
            json.dump(
                {
                    "doc_count": len(self._documents),
                    "resource_docs": len([d for d in self._documents if d["type"] == "resource"]),
                    "project_docs": len([d for d in self._documents if d["type"] == "project"]),
                    "embedding_dimension": int(embeddings.shape[1]),
                    "faiss_available": self.faiss_available,
                    "embedding_model": settings.embedding_model,
                },
                f,
                indent=2,
                ensure_ascii=True,
            )
        np.save(files["embeddings"], embeddings)

        return {
            "phase": "phase_2",
            "status": "success",
            "message": "Employee/project documents ingested, embedded, and indexed.",
            "faiss_available": self.faiss_available,
            "documents_indexed": len(self._documents),
            "resource_documents": len([d for d in self._documents if d["type"] == "resource"]),
            "project_documents": len([d for d in self._documents if d["type"] == "project"]),
            "artifacts": {
                "index": str(files["index"]),
                "documents": str(files["documents"]),
                "manifest": str(files["manifest"]),
                "embeddings": str(files["embeddings"]),
            },
        }

    def _ensure_phase2_index(self) -> None:
        if self._documents and self._embeddings is not None:
            return

        files = _phase2_files()
        documents_path = files["documents"]
        embeddings_path = files["embeddings"]

        if documents_path.exists() and embeddings_path.exists():
            with documents_path.open("r", encoding="utf-8") as f:
                self._documents = json.load(f)
            self._embeddings = np.load(embeddings_path)
            if faiss is not None and files["index"].exists():
                self._index = faiss.read_index(str(files["index"]))
            return

        self.build_phase2_rag_pipeline()

    def _search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        self._ensure_phase2_index()
        assert self._embeddings is not None

        query_embedding = self._model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
        query_embedding = np.asarray(query_embedding, dtype="float32")

        if faiss is not None and self._index is not None:
            scores, indices = self._index.search(query_embedding, min(top_k, len(self._documents)))
            ranked: List[Dict[str, Any]] = []
            for score, index in zip(scores[0], indices[0]):
                if index < 0:
                    continue
                item = dict(self._documents[index])
                item["match_score"] = float(score)
                ranked.append(item)
            return ranked

        scores = np.dot(self._embeddings, query_embedding[0])
        ranked = []
        for index in np.argsort(scores)[::-1][:top_k]:
            item = dict(self._documents[int(index)])
            item["match_score"] = float(scores[int(index)])
            ranked.append(item)
        return ranked

    def retrieve_phase3(
        self,
        staffing_request: str,
        top_k: int = 5,
        min_availability: float = 50.0,
        max_utilization: float = 50.0,
    ) -> Dict[str, Any]:
        """Phase 3: convert staffing request into embeddings and retrieve employees."""
        ranked = self._search(staffing_request, top_k=max(top_k * 2, top_k))

        employees = []
        for row in ranked:
            if row["type"] != "resource":
                continue
            if row.get("availability_percentage", 0) < min_availability:
                continue
            if row.get("utilization_percentage", 100) > max_utilization:
                continue
            employees.append({
                **row,
                "match_score": round(float(row.get("match_score", 0.0)), 4),
            })
            if len(employees) >= top_k:
                break

        return {
            "phase": "phase_3",
            "status": "success",
            "staffing_request": staffing_request,
            "filters": {
                "min_availability": min_availability,
                "max_utilization": max_utilization,
            },
            "top_matches": employees,
            "total_matches": len(employees),
        }

    def recommend_phase4(
        self,
        project_requirements: str,
        required_skills: List[str],
        team_size: int = 3,
        top_k: int = 10,
    ) -> Dict[str, Any]:
        """Phase 4: recommendation engine outputs."""
        ranked = self._search(project_requirements, top_k=max(top_k * 2, top_k))
        required = [skill.strip() for skill in required_skills if skill and skill.strip()]

        recommendations: List[Dict[str, Any]] = []
        for row in ranked:
            if row["type"] != "resource":
                continue

            resource_skills = set(row.get("skills", []))
            required_set = set(required)
            overlap = resource_skills.intersection(required_set)
            overlap_score = (len(overlap) / len(required_set)) if required_set else 0.0
            availability_score = float(row.get("availability_percentage", 0)) / 100.0
            experience_score = min(float(row.get("experience_years", 0)) / 10.0, 1.0)
            semantic_score = float(row.get("match_score", 0.0))
            final_score = round((semantic_score * 0.5) + (overlap_score * 0.35) + (availability_score * 0.1) + (experience_score * 0.05), 4)

            recommendations.append({
                "resource_id": row.get("id"),
                "name": row.get("name"),
                "department": row.get("department"),
                "skills": row.get("skills", []),
                "availability_percentage": row.get("availability_percentage", 0),
                "utilization_percentage": row.get("utilization_percentage", 0),
                "match_score": final_score,
                "match_score_breakdown": {
                    "semantic": round(semantic_score, 4),
                    "skill_overlap": round(overlap_score, 4),
                    "availability": round(availability_score, 4),
                    "experience": round(experience_score, 4),
                },
                "justification": (
                    f"Matched skills: {', '.join(sorted(overlap)) or 'none'}; "
                    f"availability: {row.get('availability_percentage', 0)}%; "
                    f"experience: {row.get('experience_years', 0)} years."
                ),
            })

        recommendations = sorted(recommendations, key=lambda x: x["match_score"], reverse=True)[:top_k]
        selected = recommendations[:team_size]
        coverage = _coverage_summary(required, selected)

        return {
            "phase": "phase_4",
            "status": "success",
            "project_requirements": project_requirements,
            "required_skills": required,
            "team_size": team_size,
            "recommended_employees": selected,
            "match_scores": [
                {"name": row["name"], "match_score": row["match_score"]}
                for row in recommendations
            ],
            "recommendation_justifications": [
                {"name": row["name"], "justification": row["justification"]}
                for row in selected
            ],
            **coverage,
        }

    def dashboard_phase5(self) -> Dict[str, Any]:
        """Phase 5: dashboard metrics and staffing recommendations."""
        self._ensure_phase2_index()

        total_resources = len(self._resources)
        available_resources = [row for row in self._resources if float(row.get("availability_percentage", 0)) > 0]
        bench_resources = [row for row in self._resources if row.get("is_on_bench")]
        bench_percentage = round((len(bench_resources) / total_resources * 100.0) if total_resources else 0.0, 1)

        demand_counts: Dict[str, int] = {}
        supply_counts: Dict[str, int] = {}
        for project in self._projects:
            for skill in project.get("required_skills", []):
                demand_counts[skill] = demand_counts.get(skill, 0) + 1
        for resource in self._resources:
            for skill in resource.get("skills", []):
                supply_counts[skill] = supply_counts.get(skill, 0) + 1

        skill_insights = []
        all_skills = sorted(set(demand_counts) | set(supply_counts))
        for skill in all_skills:
            demand = demand_counts.get(skill, 0)
            supply = supply_counts.get(skill, 0)
            skill_insights.append({
                "skill": skill,
                "demand": demand,
                "supply": supply,
                "gap": max(0, demand - supply),
            })

        skill_insights = sorted(skill_insights, key=lambda x: (x["gap"], x["demand"]), reverse=True)
        top_gaps = [item for item in skill_insights if item["gap"] > 0][:10]

        staffing_recommendations = []
        for project in sorted(self._projects, key=lambda x: (x.get("priority") == "critical", x.get("team_size_required", 0) - x.get("current_team_size", 0)), reverse=True):
            gap = max(0, int(project.get("team_size_required", 0)) - int(project.get("current_team_size", 0)))
            if gap <= 0:
                continue
            recommendation = self.recommend_phase4(
                project_requirements=project.get("description") or project.get("name", ""),
                required_skills=project.get("required_skills", []),
                team_size=min(gap, 3),
                top_k=5,
            )
            staffing_recommendations.append({
                "project_name": project.get("name"),
                "project_code": project.get("project_code"),
                "gap": gap,
                "priority": project.get("priority"),
                "top_candidates": recommendation["recommended_employees"],
            })

        return {
            "phase": "phase_5",
            "status": "success",
            "resources": {
                "total": total_resources,
                "available": len(available_resources),
                "bench": len(bench_resources),
                "bench_percentage": bench_percentage,
            },
            "skill_demand_insights": top_gaps,
            "staffing_recommendations": staffing_recommendations[:5],
            "project_gaps": [
                {
                    "project_name": project.get("name"),
                    "project_code": project.get("project_code"),
                    "gap": max(0, int(project.get("team_size_required", 0)) - int(project.get("current_team_size", 0))),
                    "priority": project.get("priority"),
                }
                for project in self._projects
                if max(0, int(project.get("team_size_required", 0)) - int(project.get("current_team_size", 0))) > 0
            ],
            "available_resources": [
                {
                    "name": row.get("name"),
                    "department": row.get("department"),
                    "availability_percentage": row.get("availability_percentage", 0),
                    "skills": row.get("skills", []),
                }
                for row in available_resources[:10]
            ],
        }


_SERVICE: Optional[PhasePipelineService] = None


def get_phase_pipeline_service() -> PhasePipelineService:
    global _SERVICE
    if _SERVICE is None:
        _SERVICE = PhasePipelineService()
    return _SERVICE
