"""
build_vector_store.py
Load employee data from PostgreSQL, generate sentence-transformer embeddings,
and persist a FAISS index for fast similarity search.
Run: python scripts/build_vector_store.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from backend.config import settings
from backend.database.orm_models import EmployeeORM
from backend.services.embedding_service import build_and_save_index


def fetch_employees() -> list[dict]:
    engine = create_engine(settings.sync_database_url, echo=False)
    with Session(engine) as session:
        employees = session.query(EmployeeORM).all()
        return [
            {
                "employee_id": e.employee_id,
                "name": e.name,
                "skills": e.skills,
                "experience_years": e.experience_years,
                "certifications": e.certifications,
                "domain": e.domain,
                "availability": e.availability,
                "availability_date": e.availability_date,
                "utilization_percent": e.utilization_percent,
                "bench_since": e.bench_since,
                "resume_text": e.resume_text,
            }
            for e in employees
        ]


if __name__ == "__main__":
    print(f"Fetching employees from PostgreSQL ({settings.sync_database_url})...")
    employees = fetch_employees()

    if not employees:
        print("No employees found. Run seed_database.py first.")
        sys.exit(1)

    print(f"Found {len(employees)} employees. Building FAISS index...\n")
    build_and_save_index(employees, settings.faiss_index_path)
    print("\nVector store build complete.")
