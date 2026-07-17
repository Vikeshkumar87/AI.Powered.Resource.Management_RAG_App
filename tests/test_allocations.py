"""
Tests for Allocation API endpoints.
"""
import pytest
from datetime import datetime, timedelta, UTC
from fastapi.testclient import TestClient


def create_resource(client, override=None):
    data = {
        "name": "Test Resource",
        "email": "resource@test.com",
        "employee_id": "RES001",
        "department": "Engineering",
        "designation": "Software Engineer",
        "skills": ["Python"],
        "experience_years": 3.0,
        "is_on_bench": True,
        "availability_percentage": 100.0,
        "certifications": [],
        "preferred_roles": [],
    }
    if override:
        data.update(override)
    res = client.post("/api/v1/resources/", json=data)
    return res.json()


def create_project(client, override=None):
    data = {
        "name": "Test Project",
        "project_code": "ALLOC_TEST_001",
        "client": "Test Client",
        "status": "active",
        "required_skills": ["Python"],
        "team_size_required": 2,
        "priority": "medium",
    }
    if override:
        data.update(override)
    res = client.post("/api/v1/projects/", json=data)
    return res.json()


class TestAllocationCRUD:
    def test_list_allocations_empty(self, client: TestClient):
        """Should return empty list with no allocations."""
        response = client.get("/api/v1/allocations/")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_allocation(self, client: TestClient):
        """Should create an allocation and update resource status."""
        resource = create_resource(client)
        project = create_project(client)

        now = datetime.now(UTC).replace(tzinfo=None).isoformat()
        end = (datetime.now(UTC).replace(tzinfo=None) + timedelta(days=90)).isoformat()

        response = client.post("/api/v1/allocations/", json={
            "resource_id": resource["id"],
            "project_id": project["id"],
            "role": "Backend Developer",
            "allocation_percentage": 100.0,
            "start_date": now,
            "end_date": end,
        })
        assert response.status_code == 201
        data = response.json()
        assert data["resource_id"] == resource["id"]
        assert data["project_id"] == project["id"]
        assert data["role"] == "Backend Developer"
        assert data["is_active"] is True

    def test_allocation_updates_resource_bench_status(self, client: TestClient):
        """Creating an allocation should move resource off bench."""
        resource = create_resource(client)
        project = create_project(client)

        now = datetime.now(UTC).replace(tzinfo=None).isoformat()
        client.post("/api/v1/allocations/", json={
            "resource_id": resource["id"],
            "project_id": project["id"],
            "role": "Developer",
            "allocation_percentage": 100.0,
            "start_date": now,
        })

        updated_resource = client.get(f"/api/v1/resources/{resource['id']}").json()
        assert updated_resource["is_on_bench"] is False
        assert updated_resource["availability_percentage"] == 0.0

    def test_over_allocation_rejected(self, client: TestClient):
        """Should reject allocation exceeding 100%."""
        resource = create_resource(client)
        project = create_project(client)
        project2 = create_project(client, override={"project_code": "ALLOC_TEST_002"})

        now = datetime.now(UTC).replace(tzinfo=None).isoformat()
        # First allocation: 80%
        client.post("/api/v1/allocations/", json={
            "resource_id": resource["id"],
            "project_id": project["id"],
            "role": "Developer",
            "allocation_percentage": 80.0,
            "start_date": now,
        })

        # Second allocation: 30% (would exceed 100%)
        response = client.post("/api/v1/allocations/", json={
            "resource_id": resource["id"],
            "project_id": project2["id"],
            "role": "Consultant",
            "allocation_percentage": 30.0,
            "start_date": now,
        })
        assert response.status_code == 400

    def test_partial_allocation(self, client: TestClient):
        """Should allow partial allocation (< 100%)."""
        resource = create_resource(client)
        project = create_project(client)

        now = datetime.now(UTC).replace(tzinfo=None).isoformat()
        response = client.post("/api/v1/allocations/", json={
            "resource_id": resource["id"],
            "project_id": project["id"],
            "role": "Part-time Consultant",
            "allocation_percentage": 50.0,
            "start_date": now,
        })
        assert response.status_code == 201

        updated_resource = client.get(f"/api/v1/resources/{resource['id']}").json()
        assert updated_resource["availability_percentage"] == 50.0

    def test_delete_allocation_returns_to_bench(self, client: TestClient):
        """Deleting the only allocation should return resource to bench."""
        resource = create_resource(client)
        project = create_project(client)

        now = datetime.now(UTC).replace(tzinfo=None).isoformat()
        alloc = client.post("/api/v1/allocations/", json={
            "resource_id": resource["id"],
            "project_id": project["id"],
            "role": "Developer",
            "allocation_percentage": 100.0,
            "start_date": now,
        }).json()

        client.delete(f"/api/v1/allocations/{alloc['id']}")

        updated_resource = client.get(f"/api/v1/resources/{resource['id']}").json()
        assert updated_resource["is_on_bench"] is True
        assert updated_resource["availability_percentage"] == 100.0

    def test_allocation_invalid_resource(self, client: TestClient):
        """Should return 404 for non-existent resource."""
        project = create_project(client)
        response = client.post("/api/v1/allocations/", json={
            "resource_id": 99999,
            "project_id": project["id"],
            "role": "Developer",
            "allocation_percentage": 100.0,
            "start_date": datetime.now(UTC).replace(tzinfo=None).isoformat(),
        })
        assert response.status_code == 404

    def test_allocation_invalid_project(self, client: TestClient):
        """Should return 404 for non-existent project."""
        resource = create_resource(client)
        response = client.post("/api/v1/allocations/", json={
            "resource_id": resource["id"],
            "project_id": 99999,
            "role": "Developer",
            "allocation_percentage": 100.0,
            "start_date": datetime.now(UTC).replace(tzinfo=None).isoformat(),
        })
        assert response.status_code == 404
