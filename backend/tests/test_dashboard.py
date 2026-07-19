"""
Tests for Dashboard API endpoints.
"""
import pytest
from fastapi.testclient import TestClient


def seed_resources(client):
    """Helper to create sample resources."""
    resources = [
        {
            "name": "Alice Smith",
            "email": "alice@test.com",
            "employee_id": "D001",
            "department": "Engineering",
            "designation": "Software Engineer",
            "skills": ["Python", "Docker"],
            "experience_years": 3.0,
            "is_on_bench": True,
            "availability_percentage": 100.0,
            "certifications": [],
            "preferred_roles": [],
        },
        {
            "name": "Bob Jones",
            "email": "bob@test.com",
            "employee_id": "D002",
            "department": "QA",
            "designation": "QA Engineer",
            "skills": ["Selenium"],
            "experience_years": 2.0,
            "is_on_bench": False,
            "availability_percentage": 0.0,
            "certifications": [],
            "preferred_roles": [],
        },
    ]
    return [client.post("/api/v1/resources/", json=r).json() for r in resources]


def seed_project(client):
    """Helper to create a sample project."""
    return client.post("/api/v1/projects/", json={
        "name": "Test Project",
        "project_code": "DASH_TEST_001",
        "client": "Dash Client",
        "status": "active",
        "required_skills": ["Python"],
        "team_size_required": 3,
        "priority": "high",
    }).json()


class TestDashboardStats:
    def test_stats_empty_database(self, client: TestClient):
        """Should return zeros for empty database."""
        response = client.get("/api/v1/dashboard/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["resources"]["total"] == 0
        assert data["resources"]["on_bench"] == 0
        assert data["projects"]["total"] == 0

    def test_stats_with_data(self, client: TestClient):
        """Should reflect correct counts with data."""
        seed_resources(client)
        seed_project(client)

        response = client.get("/api/v1/dashboard/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["resources"]["total"] == 2
        assert data["resources"]["on_bench"] == 1
        assert data["resources"]["allocated"] == 1
        assert data["projects"]["total"] == 1
        assert data["projects"]["active"] == 1

    def test_stats_includes_top_skills(self, client: TestClient):
        """Should include top skills list."""
        seed_resources(client)
        response = client.get("/api/v1/dashboard/stats")
        data = response.json()
        assert "top_skills" in data
        assert isinstance(data["top_skills"], list)

    def test_stats_includes_departments(self, client: TestClient):
        """Should include department breakdown."""
        seed_resources(client)
        response = client.get("/api/v1/dashboard/stats")
        data = response.json()
        assert "departments" in data
        assert "Engineering" in data["departments"]
        assert data["departments"]["Engineering"] == 1


class TestBenchAging:
    def test_bench_aging_empty(self, client: TestClient):
        """Should return empty list with no bench resources."""
        response = client.get("/api/v1/dashboard/bench-aging")
        assert response.status_code == 200
        assert response.json() == []

    def test_bench_aging_returns_bench_only(self, client: TestClient):
        """Should only return bench resources."""
        resources = seed_resources(client)
        response = client.get("/api/v1/dashboard/bench-aging")
        assert response.status_code == 200
        data = response.json()
        # Only Alice (bench) should appear
        assert len(data) == 1
        assert data[0]["name"] == "Alice Smith"

    def test_bench_aging_category(self, client: TestClient):
        """Should categorize aging based on days on bench."""
        response = client.get("/api/v1/dashboard/bench-aging")
        assert response.status_code == 200


class TestProjectGaps:
    def test_project_gaps_empty(self, client: TestClient):
        """Should return empty list with no projects."""
        response = client.get("/api/v1/dashboard/project-gaps")
        assert response.status_code == 200
        assert response.json() == []

    def test_project_gaps_shows_underfilled(self, client: TestClient):
        """Should show projects with fewer team members than required."""
        seed_project(client)  # team_size_required=3, current=0
        response = client.get("/api/v1/dashboard/project-gaps")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["gap"] == 3

    def test_project_gaps_excludes_completed(self, client: TestClient):
        """Should not show completed projects."""
        client.post("/api/v1/projects/", json={
            "name": "Completed Proj",
            "project_code": "COMP001",
            "client": "Client",
            "status": "completed",
            "required_skills": [],
            "team_size_required": 5,
            "priority": "low",
        })
        response = client.get("/api/v1/dashboard/project-gaps")
        assert response.status_code == 200
        assert response.json() == []
