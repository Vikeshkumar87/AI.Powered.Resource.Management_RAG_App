"""
Tests for Project API endpoints.
"""
import pytest
from fastapi.testclient import TestClient


class TestProjectCRUD:
    def test_list_projects_empty(self, client: TestClient):
        """Should return empty list when no projects exist."""
        response = client.get("/api/v1/projects/")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["projects"] == []

    def test_create_project(self, client: TestClient, sample_project_data):
        """Should create a project and return 201."""
        response = client.post("/api/v1/projects/", json=sample_project_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_project_data["name"]
        assert data["project_code"] == sample_project_data["project_code"]
        assert data["client"] == sample_project_data["client"]
        assert data["status"] == "planning"
        assert "id" in data

    def test_create_project_duplicate_code(self, client: TestClient, sample_project_data):
        """Should reject duplicate project code."""
        client.post("/api/v1/projects/", json=sample_project_data)
        response = client.post("/api/v1/projects/", json=sample_project_data)
        assert response.status_code == 400

    def test_get_project(self, client: TestClient, sample_project_data):
        """Should get a project by ID."""
        create_res = client.post("/api/v1/projects/", json=sample_project_data)
        project_id = create_res.json()["id"]

        response = client.get(f"/api/v1/projects/{project_id}")
        assert response.status_code == 200
        assert response.json()["id"] == project_id

    def test_get_project_not_found(self, client: TestClient):
        """Should return 404 for non-existent project."""
        response = client.get("/api/v1/projects/99999")
        assert response.status_code == 404

    def test_update_project(self, client: TestClient, sample_project_data):
        """Should update project fields."""
        create_res = client.post("/api/v1/projects/", json=sample_project_data)
        project_id = create_res.json()["id"]

        update = {"status": "active", "priority": "critical"}
        response = client.put(f"/api/v1/projects/{project_id}", json=update)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "active"
        assert data["priority"] == "critical"
        # Unchanged fields should remain
        assert data["name"] == sample_project_data["name"]

    def test_delete_project(self, client: TestClient, sample_project_data):
        """Should delete a project."""
        create_res = client.post("/api/v1/projects/", json=sample_project_data)
        project_id = create_res.json()["id"]

        response = client.delete(f"/api/v1/projects/{project_id}")
        assert response.status_code == 204

        get_response = client.get(f"/api/v1/projects/{project_id}")
        assert get_response.status_code == 404

    def test_list_projects_filter_by_status(self, client: TestClient, sample_project_data):
        """Should filter projects by status."""
        client.post("/api/v1/projects/", json=sample_project_data)
        active = {**sample_project_data, "project_code": "ACTIVE001", "status": "active"}
        client.post("/api/v1/projects/", json=active)

        response = client.get("/api/v1/projects/?status=active")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["projects"][0]["status"] == "active"

    def test_get_project_team_empty(self, client: TestClient, sample_project_data):
        """Should return empty team for a new project."""
        create_res = client.post("/api/v1/projects/", json=sample_project_data)
        project_id = create_res.json()["id"]

        response = client.get(f"/api/v1/projects/{project_id}/team")
        assert response.status_code == 200
        assert response.json() == []
