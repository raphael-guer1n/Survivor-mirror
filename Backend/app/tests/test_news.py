from unittest.mock import patch, MagicMock

news_row = {
    "id": 1,
    "title": "Big News",
    "news_date": "2025-01-01",
    "location": "Paris",
    "category": "Tech",
    "startup_id": 1,
    "description": "desc",
    "image_s3_key": None,
}

def test_get_news(client):
    with patch("app.routers.news.get_connection") as mock_conn:
        cur = MagicMock()
        cur.fetchall.return_value = [news_row]
        mock_conn.return_value.cursor.return_value = cur
        r = client.get("/api/news/")
        assert r.status_code == 200
        assert r.json()[0]["title"] == "Big News"

def test_get_news_item_not_found(client):
    with patch("app.routers.news.get_connection") as mock_conn:
        cur = MagicMock()
        cur.fetchone.return_value = None
        mock_conn.return_value.cursor.return_value = cur
        r = client.get("/api/news/999")
        assert r.status_code == 404
