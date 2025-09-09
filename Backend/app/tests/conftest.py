import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
from app.routers import auth

@pytest.fixture(scope="session", autouse=True)
def disable_scheduler():
    with patch("app.scheduler.sync_runner.register_scheduler"):
        yield

@pytest.fixture(scope="session")
def client():
    app.dependency_overrides[auth.require_admin] = lambda: {"id": 99, "role": "admin"}
    with TestClient(app) as c:
        yield c
