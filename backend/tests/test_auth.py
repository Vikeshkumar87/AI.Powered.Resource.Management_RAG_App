"""
Tests for authentication endpoints.
"""


class TestAuth:
    def test_admin_login_returns_token(self, client):
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "admin123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "admin"
        assert data["token_type"] == "bearer"
        assert data["access_token"]

    def test_user_login_returns_token(self, client):
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "user", "password": "user123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "user"
        assert data["access_token"]

    def test_admin_route_accepts_role_header(self, client):
        response = client.post(
            "/api/v1/admin/phase1/prepare-data",
            headers={"X-User-Role": "admin"},
        )
        assert response.status_code == 200
