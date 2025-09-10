from unittest.mock import patch, MagicMock
from app.utils.jwt import create_access_token
from app.utils.security import hash_password

def test_request_register_success(client):
    with patch("app.routers.auth.get_connection") as mock_conn, \
         patch("app.routers.auth.send_verification_email") as mock_email:
        cursor = MagicMock()
        cursor.fetchone.return_value = None
        mock_conn.return_value.cursor.return_value = cursor
        resp = client.post("/auth/request-register", json={"email": "new@example.com"})
        assert resp.status_code == 200
        assert "Code sent" in resp.json()["detail"]

def test_request_register_conflict(client):
    with patch("app.routers.auth.get_connection") as mock_conn:
        cursor = MagicMock()
        cursor.fetchone.return_value = {"id": 1, "password_hash": "x"}
        mock_conn.return_value.cursor.return_value = cursor
        resp = client.post("/auth/request-register", json={"email": "exist@example.com"})
        assert resp.status_code == 409

def test_verify_code_invalid(client):
    with patch("app.routers.auth.get_connection") as mock_conn:
        cursor = MagicMock()
        cursor.fetchone.return_value = None
        mock_conn.return_value.cursor.return_value = cursor
        resp = client.post("/auth/verify-register-code", json={"email": "a@b.com", "code": "123"})
        assert "Wrong code" in resp.json()["detail"]

def test_complete_register_missing_fields(client):
    resp = client.post("/auth/complete-register", json={"email": "a@b.com", "code": "123"})
    assert resp.status_code == 400
    assert "Missing required field" in resp.json()["detail"]

def test_login_and_me(client):
    pw_hash = hash_password("pass")
    with patch("app.routers.auth.get_connection") as mock_conn:
        cursor = MagicMock()
        cursor.fetchone.return_value = {
            "id": 1, "email": "x@y.com",
            "name": "User", "role": "user",
            "password_hash": pw_hash,
        }
        mock_conn.return_value.cursor.return_value = cursor
        resp = client.post("/auth/login", json={"email": "x@y.com", "password": "pass"})
        assert resp.status_code == 200
        token = resp.json()["access_token"]
        resp2 = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert resp2.status_code == 200
        assert resp2.json()["email"] == "x@y.com"
