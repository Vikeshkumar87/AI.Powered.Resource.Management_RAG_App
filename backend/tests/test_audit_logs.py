"""
Tests for audit logging.
"""


def test_audit_logs_capture_login_and_admin_actions(client):
    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    assert login_response.status_code == 200

    seed_response = client.post(
        "/api/v1/admin/seed?clear_existing=false",
        headers={"X-User-Role": "admin"},
    )
    assert seed_response.status_code == 200

    audit_response = client.get(
        "/api/v1/admin/audit-logs?limit=10",
        headers={"X-User-Role": "admin"},
    )
    assert audit_response.status_code == 200
    data = audit_response.json()
    actions = [entry["action"] for entry in data["entries"]]
    assert "login_success" in actions
    assert "seed_database" in actions
