import os
from pathlib import Path
from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=ENV_PATH)

def env(name: str, cast=None, default=None, required: bool = True):
    val = os.getenv(name)
    if val is None:
        if required and default is None:
            raise RuntimeError(f"Missing environment variable: {name}")
        return default
    return cast(val) if cast else val

DB_HOST = env("DB_HOST")
DB_PORT = env("DB_PORT", int)
DB_USER = env("DB_USER")
DB_PASSWORD = env("DB_PASSWORD")
DB_NAME = env("DB_NAME")

BCRYPT_ROUNDS = env("BCRYPT_ROUNDS", int)

JEB_API_BASE_URL = env("JEB_API_BASE_URL")
JEB_API_KEY = env("JEB_API_KEY")
JEB_API_TIMEOUT = env("JEB_API_TIMEOUT", float)

SYNC_INTERVAL_SECONDS = env("SYNC_INTERVAL_SECONDS", int)