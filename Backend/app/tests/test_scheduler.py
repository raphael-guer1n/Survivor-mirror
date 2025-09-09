from unittest.mock import patch
from fastapi import FastAPI
from app.scheduler.sync_runner import register_scheduler

def test_register_scheduler_calls_sync():
    app = FastAPI()
    with patch("app.scheduler.sync_runner.sync_all") as mock_sync:
        register_scheduler(app)
        for h in app.router.on_startup:
            h()
        mock_sync.assert_called()
