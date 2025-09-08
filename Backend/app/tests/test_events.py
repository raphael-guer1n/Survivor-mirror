from unittest.mock import patch, MagicMock

event_row = {
    "id": 1,
    "name": "TechConf",
    "dates": "2025-09-01",
    "location": "Berlin",
    "description": "desc",
    "event_type": "conference",
    "target_audience": "startups",
    "image_s3_key": None,
}

def test_get_events(client):
    with patch("app.routers.events.get_connection") as mock_conn:
        cur = MagicMock()
        cur.fetchall.return_value = [event_row]
        mock_conn.return_value.cursor.return_value = cur
        r = client.get("/api/events/")
        assert r.status_code == 200
        assert r.json()[0]["name"] == "TechConf"

def test_get_event_not_found(client):
    with patch("app.routers.events.get_connection") as mock_conn:
        cur = MagicMock()
        cur.fetchone.return_value = None
        mock_conn.return_value.cursor.return_value = cur
        r = client.get("/api/events/123")
        assert r.status_code == 404
