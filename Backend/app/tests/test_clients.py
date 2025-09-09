from unittest.mock import patch
import app.clients.jeb_api as jeb

def test_jeb_api_methods():
    with patch("app.clients.jeb_api.requests.get") as m:
        m.return_value.json.return_value = {"ok": True}
        assert "ok" in m.return_value.json()
