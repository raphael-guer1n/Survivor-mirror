from unittest.mock import patch, MagicMock

investor_row = {
    "id": 1,
    "name": "Investor A",
    "legal_status": None,
    "address": None,
    "email": "investor@example.com",
    "phone": None,
    "created_at": None,
    "description": "desc",
    "investor_type": "VC",
    "investment_focus": "tech",
    "image_s3_key": None,
}

def test_get_investors(client):
    with patch("app.routers.investors.get_connection") as mock_conn:
        cur = MagicMock()
        cur.fetchall.return_value = [investor_row]
        mock_conn.return_value.cursor.return_value = cur
        r = client.get("/api/investors/")
        assert r.status_code == 200
        assert r.json()[0]["email"] == "investor@example.com"

def test_get_investor_not_found(client):
    with patch("app.routers.investors.get_connection") as mock_conn:
        cur = MagicMock()
        cur.fetchone.return_value = None
        mock_conn.return_value.cursor.return_value = cur
        r = client.get("/api/investors/404")
        assert r.status_code == 404
