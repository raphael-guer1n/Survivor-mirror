from datetime import timedelta
from app.utils.jwt import create_access_token, decode_access_token

def test_jwt_ok():
    t = create_access_token({"sub": "1"}, expires_delta=timedelta(seconds=1))
    d = decode_access_token(t)
    assert d["sub"] == "1"

def test_jwt_invalid():
    assert decode_access_token("bad") is None
