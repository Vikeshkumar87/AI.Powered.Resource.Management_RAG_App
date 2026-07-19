"""
Phase 1 data preparation utilities.

Phase 1 goals:
- Collect employee and project data
- Standardize skill names via taxonomy
- Store prepared artifacts in JSON format
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple
import json

try:
    # Runtime path when executed through backend/run.py
    from app.data.sample_data import get_sample_projects, get_sample_resources
except ModuleNotFoundError:
    # Package path when imported as backend.app.data.*
    from backend.app.data.sample_data import get_sample_projects, get_sample_resources


SKILL_TAXONOMY: Dict[str, Any] = {
    "version": "1.0",
    "domains": {
        "backend": [
            "Python",
            "FastAPI",
            "Django",
            "Java",
            "Spring Boot",
            "Go",
            "Node.js",
            "Microservices",
            "gRPC",
            "REST APIs",
        ],
        "frontend": [
            "React",
            "Vue.js",
            "TypeScript",
            "CSS3",
            "Webpack",
            "GraphQL",
            "Jest",
            "Cypress",
        ],
        "data_ai": [
            "Machine Learning",
            "NLP",
            "TensorFlow",
            "PyTorch",
            "Scikit-learn",
            "Spark",
            "MLflow",
            "Feature Engineering",
            "Data Analysis",
            "Data Visualization",
        ],
        "cloud_devops": [
            "AWS",
            "Azure",
            "GCP",
            "Docker",
            "Kubernetes",
            "Terraform",
            "Jenkins",
            "CloudFormation",
            "AWS SageMaker",
            "Linux",
        ],
        "database": [
            "SQL",
            "PostgreSQL",
            "MySQL",
            "MongoDB",
            "Redis",
            "Core Data",
        ],
        "mobile": [
            "Swift",
            "SwiftUI",
            "Objective-C",
            "Kotlin",
            "Android SDK",
            "Jetpack Compose",
            "React Native",
            "Xcode",
            "Firebase",
        ],
        "quality_security": [
            "Selenium",
            "JMeter",
            "Postman",
            "JIRA",
            "TestRail",
            "Penetration Testing",
            "OWASP",
            "SIEM",
            "Security",
            "Compliance",
            "AWS Security",
        ],
        "product_management": [
            "Product Strategy",
            "Agile",
            "Scrum",
            "User Research",
            "Networking",
        ],
    },
    "synonyms": {
        "rest api": "REST APIs",
        "rest apis": "REST APIs",
        "k8s": "Kubernetes",
        "postgres": "PostgreSQL",
        "postgresql": "PostgreSQL",
        "ml": "Machine Learning",
        "nlp": "NLP",
        "js": "Node.js",
        "google cloud": "GCP",
        "google cloud platform": "GCP",
        "terraform": "Terraform",
        "aws sagemaker": "AWS SageMaker",
    },
}


def _canonical_skill(skill: str) -> str:
    raw = skill.strip()
    if not raw:
        return raw

    lookup = raw.lower()
    if lookup in SKILL_TAXONOMY["synonyms"]:
        return SKILL_TAXONOMY["synonyms"][lookup]

    for domain_skills in SKILL_TAXONOMY["domains"].values():
        for canonical in domain_skills:
            if canonical.lower() == lookup:
                return canonical

    return raw


def _standardize_skill_list(skills: List[str]) -> List[str]:
    seen = set()
    normalized: List[str] = []
    for skill in skills or []:
        canonical = _canonical_skill(skill)
        if canonical and canonical not in seen:
            normalized.append(canonical)
            seen.add(canonical)
    return normalized


def _to_json_value(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, list):
        return [_to_json_value(v) for v in value]
    if isinstance(value, dict):
        return {k: _to_json_value(v) for k, v in value.items()}
    return value


def _prepare_resources(resources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    prepared: List[Dict[str, Any]] = []
    for row in resources:
        entry = dict(row)
        entry["skills"] = _standardize_skill_list(entry.get("skills", []))
        prepared.append(_to_json_value(entry))
    return prepared


def _prepare_projects(projects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    prepared: List[Dict[str, Any]] = []
    for row in projects:
        entry = dict(row)
        entry["required_skills"] = _standardize_skill_list(entry.get("required_skills", []))
        prepared.append(_to_json_value(entry))
    return prepared


def prepare_phase1_data() -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Collect and standardize employee/project data for phase 1."""
    resources = _prepare_resources(get_sample_resources())
    projects = _prepare_projects(get_sample_projects())
    return resources, projects


def save_phase1_json(output_dir: Path | None = None) -> Dict[str, Any]:
    """Save phase 1 artifacts as JSON files and return summary metadata."""
    if output_dir is None:
        output_dir = Path(__file__).resolve().parent / "phase1_json"

    output_dir.mkdir(parents=True, exist_ok=True)

    resources, projects = prepare_phase1_data()

    employees_path = output_dir / "employees.json"
    projects_path = output_dir / "projects.json"
    taxonomy_path = output_dir / "skill_taxonomy.json"

    with employees_path.open("w", encoding="utf-8") as f:
        json.dump(resources, f, indent=2, ensure_ascii=True)

    with projects_path.open("w", encoding="utf-8") as f:
        json.dump(projects, f, indent=2, ensure_ascii=True)

    with taxonomy_path.open("w", encoding="utf-8") as f:
        json.dump(SKILL_TAXONOMY, f, indent=2, ensure_ascii=True)

    return {
        "employees_count": len(resources),
        "projects_count": len(projects),
        "taxonomy_domains": len(SKILL_TAXONOMY["domains"]),
        "output_dir": str(output_dir),
        "files": {
            "employees": str(employees_path),
            "projects": str(projects_path),
            "skill_taxonomy": str(taxonomy_path),
        },
    }
