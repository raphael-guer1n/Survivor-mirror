import os
from app.core import config

def test_env(monkeypatch):
    monkeypatch.setenv("X", "123")
    assert config.env("X") == "123"
    assert config.env("Y", default="z") == "z"
