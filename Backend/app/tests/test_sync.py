from unittest.mock import patch, MagicMock
from app.services import sync

def test_sync_all_runs():
    def fake_get(url, *args, **kwargs):
        resp = MagicMock()
        resp.raise_for_status.return_value = None
        if "/news/" in url and "?" not in url:
            resp.json.return_value = {
                "id": 1,
                "title": "Fake News",
                "news_date": "2025-01-01",
                "location": "Paris",
                "category": "Tech",
                "startup_id": 1,
                "description": "desc"
            }
        elif "/news" in url:
            resp.json.return_value = [{"id": 1}]
        elif "/startups" in url:
            resp.json.return_value = [{"id": 1, "name": "Fake Startup", "email": "s@x.com"}]
        else:
            resp.json.return_value = {}
        return resp

    with patch("app.services.sync.get_connection"), \
         patch("app.services.sync.SyncService._get_last_synced", return_value=0), \
         patch("app.utils.s3.upload_file_to_s3", return_value="mock-url"), \
         patch("app.utils.s3.generate_presigned_url", return_value="mock-url"), \
         patch("app.utils.s3.delete_file_from_s3", return_value=None), \
         patch("app.services.sync.requests.get", side_effect=fake_get), \
         patch("app.services.sync.requests.post", return_value=MagicMock()), \
         patch("app.services.sync.requests.put", return_value=MagicMock()), \
         patch("app.services.sync.requests.delete", return_value=MagicMock()):
        sync.sync_all()
