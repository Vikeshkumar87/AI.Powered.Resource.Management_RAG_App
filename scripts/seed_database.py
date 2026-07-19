"""
seed_database.py
Load JSON seed data from data/ into PostgreSQL via SQLAlchemy (sync psycopg2).
Run: python scripts/seed_database.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from backend.config import settings
from backend.database.orm_models import EmployeeORM, ProjectORM, AllocationORM

# Use sync driver for simple seed script
engine = create_engine(settings.sync_database_url, echo=False)

# Import Base to create tables
from backend.database.postgresql import Base  # noqa
Base.metadata.create_all(engine)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def load_json(filename: str) -> list:
    with open(os.path.join(DATA_DIR, filename), "r", encoding="utf-8") as f:
        return json.load(f)


def seed():
    with Session(engine) as session:
        # Clear existing data (in FK-safe order)
        session.execute(text("DELETE FROM allocations"))
        session.execute(text("DELETE FROM projects"))
        session.execute(text("DELETE FROM employees"))
        session.commit()

        # Seed employees
        employees = load_json("employees.json")
        session.add_all([EmployeeORM(**e) for e in employees])
        session.commit()
        print(f"  Seeded {len(employees):>3} records → 'employees'")

        # Seed projects
        projects = load_json("projects.json")
        session.add_all([ProjectORM(**p) for p in projects])
        session.commit()
        print(f"  Seeded {len(projects):>3} records → 'projects'")

        # Seed allocations
        allocations = load_json("allocations.json")
        session.add_all([AllocationORM(**a) for a in allocations])
        session.commit()
        print(f"  Seeded {len(allocations):>3} records → 'allocations'")

    print("\nDatabase seeding complete.")


if __name__ == "__main__":
    print(f"Connecting to PostgreSQL: {settings.sync_database_url}\n")
    seed()
