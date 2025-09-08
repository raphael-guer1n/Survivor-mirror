from unittest.mock import patch, MagicMock

user_row = {
    "id": 1,
    "email": "user@example.com",
    "name": "User A",
    "role": "user",
    "founder_id": None,
    "investor_id": None,
    "image_s3_key": None,
}

def test_get_users(client):
    with patch("app.routers.users.get_connection") as mock_conn:
        cur = MagicMock()
        cur.fetchall.return_value = [user_row]
        mock_conn.return_value.cursor.return_value = cur
        r = client.get("/api/users/")
        assert r.status_code == 200
        assert r.json()[0]["email"] == "user@example.com"

def test_get_user_not_found(client):
    with patch("app.routers.users.get_connection") as mock_conn:
        cur = MagicMock()
        cur.fetchone.return_value = None
        mock_conn.return_value.cursor.return_value = cur
        r = client.get("/api/users/42")
        assert r.status_code == 404
