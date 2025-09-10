from unittest.mock import patch, MagicMock

partner_row = {
    "id": 1,
    "name": "Partner A",
    "legal_status": None,
    "address": None,
    "email": "partner@example.com",
    "phone": None,
    "partnership_type": "tech",
    "created_at": None,
    "description": "desc",
    "image_s3_key": None,
}

def test_get_partners(client):
    with patch("app.routers.partners.get_connection") as mock_conn:
        cur = MagicMock()
        cur.fetchall.return_value = [partner_row]
        mock_conn.return_value.cursor.return_value = cur
        r = client.get("/api/partners/")
        assert r.status_code == 200
        assert r.json()[0]["email"] == "partner@example.com"

def test_get_partner_not_found(client):
    with patch("app.routers.partners.get_connection") as mock_conn:
        cur = MagicMock()
        cur.fetchone.return_value = None
        mock_conn.return_value.cursor.return_value = cur
        r = client.get("/api/partners/42")
        assert r.status_code == 404
