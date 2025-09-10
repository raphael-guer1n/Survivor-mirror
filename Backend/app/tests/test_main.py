from unittest.mock import patch

def test_root_and_admin(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "Welcome" in r.json()["message"]

    with patch("app.main.sync_all", return_value={"ok": True}):
        r = client.post("/admin/sync")
        assert r.status_code == 200
        assert r.json() == {"ok": True}
