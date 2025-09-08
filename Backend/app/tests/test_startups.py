from unittest.mock import patch, MagicMock

valid_row = {
    "id": 1,
    "name": "Startup X",
    "legal_status": None,
    "address": None,
    "email": "s@x.com",
    "phone": None,
    "sector": None,
    "maturity": None,
    "created_at": None,
    "description": None,
    "website_url": None,
    "social_media_url": None,
    "project_status": None,
    "needs": None,
    "image_s3_key": None
}

def test_get_startups(client):
    with patch("app.routers.startups.get_connection") as mock_conn:
        cur = MagicMock()
        cur.fetchall.return_value = [valid_row]
        mock_conn.return_value.cursor.return_value = cur
        r = client.get("/api/startups/")
        assert r.status_code == 200

def test_get_startup_notfound(client):
    with patch("app.routers.startups.get_connection") as mock_conn:
        cur = MagicMock()
        cur.fetchone.return_value = None
        mock_conn.return_value.cursor.return_value = cur
        r = client.get("/api/startups/99")
        assert r.status_code == 404
