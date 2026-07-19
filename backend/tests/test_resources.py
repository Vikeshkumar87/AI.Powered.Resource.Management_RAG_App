"""
Tests for Resource API endpoints.
"""
import pytest
from fastapi.testclient import TestClient


class TestResourceCRUD:
    def test_list_resources_empty(self, client: TestClient):
        """Should return empty list when no resources exist."""
        response = client.get("/api/v1/resources/")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["resources"] == []

    def test_create_resource(self, client: TestClient, sample_resource_data):
        """Should create a resource and return 201."""
        response = client.post("/api/v1/resources/", json=sample_resource_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_resource_data["name"]
        assert data["email"] == sample_resource_data["email"]
        assert data["employee_id"] == sample_resource_data["employee_id"]
        assert data["is_on_bench"] is True
        assert "id" in data

    def test_create_resource_duplicate_email(self, client: TestClient, sample_resource_data):
        """Should reject duplicate email."""
        client.post("/api/v1/resources/", json=sample_resource_data)
        response = client.post("/api/v1/resources/", json=sample_resource_data)
        assert response.status_code == 400

    def test_create_resource_duplicate_employee_id(self, client: TestClient, sample_resource_data):
        """Should reject duplicate employee_id."""
        client.post("/api/v1/resources/", json=sample_resource_data)
        dup = {**sample_resource_data, "email": "other@example.com"}
        response = client.post("/api/v1/resources/", json=dup)
        assert response.status_code == 400

    def test_get_resource(self, client: TestClient, sample_resource_data):
        """Should get a resource by ID."""
        create_res = client.post("/api/v1/resources/", json=sample_resource_data)
        resource_id = create_res.json()["id"]

        response = client.get(f"/api/v1/resources/{resource_id}")
        assert response.status_code == 200
        assert response.json()["id"] == resource_id

    def test_get_resource_not_found(self, client: TestClient):
        """Should return 404 for non-existent resource."""
        response = client.get("/api/v1/resources/99999")
        assert response.status_code == 404

    def test_update_resource(self, client: TestClient, sample_resource_data):
        """Should update resource fields."""
        create_res = client.post("/api/v1/resources/", json=sample_resource_data)
        resource_id = create_res.json()["id"]

        update = {"designation": "Senior Software Engineer", "experience_years": 6.0}
        response = client.put(f"/api/v1/resources/{resource_id}", json=update)
        assert response.status_code == 200
        data = response.json()
        assert data["designation"] == "Senior Software Engineer"
        assert data["experience_years"] == 6.0
        # Unchanged fields should remain
        assert data["name"] == sample_resource_data["name"]

    def test_delete_resource(self, client: TestClient, sample_resource_data):
        """Should delete a resource."""
        create_res = client.post("/api/v1/resources/", json=sample_resource_data)
        resource_id = create_res.json()["id"]

        response = client.delete(f"/api/v1/resources/{resource_id}")
        assert response.status_code == 204

        get_response = client.get(f"/api/v1/resources/{resource_id}")
        assert get_response.status_code == 404

    def test_list_resources_with_filter(self, client: TestClient, sample_resource_data):
        """Should filter resources by department."""
        client.post("/api/v1/resources/", json=sample_resource_data)
        other = {**sample_resource_data, "email": "other@test.com", "employee_id": "TEST002",
                 "department": "QA"}
        client.post("/api/v1/resources/", json=other)

        response = client.get("/api/v1/resources/?department=Engineering")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["resources"][0]["department"] == "Engineering"


class TestBenchEndpoint:
    def test_get_bench_resources(self, client: TestClient, sample_resource_data):
        """Should return only bench resources."""
        # Create a bench resource
        client.post("/api/v1/resources/", json=sample_resource_data)
        # Create an allocated resource
        allocated = {**sample_resource_data, "email": "alloc@test.com",
                     "employee_id": "TEST002", "is_on_bench": False}
        client.post("/api/v1/resources/", json=allocated)

        response = client.get("/api/v1/resources/bench")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["resources"][0]["is_on_bench"] is True

    def test_bench_filter_by_department(self, client: TestClient, sample_resource_data):
        """Should filter bench resources by department."""
        client.post("/api/v1/resources/", json=sample_resource_data)
        other = {**sample_resource_data, "email": "qa@test.com",
                 "employee_id": "TEST002", "department": "QA", "is_on_bench": True}
        client.post("/api/v1/resources/", json=other)

        response = client.get("/api/v1/resources/bench?department=QA")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["resources"][0]["department"] == "QA"


class TestResourceAllocation:
    def test_release_resource(self, client: TestClient, sample_resource_data):
        """Should move resource to bench when released."""
        create_res = client.post("/api/v1/resources/", json=sample_resource_data)
        resource_id = create_res.json()["id"]

        response = client.post(f"/api/v1/resources/{resource_id}/release")
        assert response.status_code == 200
        data = response.json()
        assert data["is_on_bench"] is True
        assert data["availability_percentage"] == 100.0
