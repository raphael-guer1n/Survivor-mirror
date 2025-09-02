import requests
from fastapi import HTTPException
from app.core.config import JEB_API_BASE_URL, JEB_API_KEY, JEB_API_TIMEOUT

_session = requests.Session()
_session.headers.update({"X-Group-Authorization": JEB_API_KEY})

def _url(path: str) -> str:
    return f"{JEB_API_BASE_URL.rstrip('/')}/{path.lstrip('/')}"

def get_page(path: str, params: dict | None = None) -> list[dict]:
    try:
        r = _session.get(_url(path), params=params, timeout=JEB_API_TIMEOUT)
        if r.status_code == 422:
            raise HTTPException(status_code=422, detail=r.json())
        if not r.ok:
            raise HTTPException(status_code=r.status_code, detail=r.text)
        data = r.json()
        if isinstance(data, list):
            return data
        return [data]
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Upstream JEB API error: {e}")

def get_one(path: str) -> dict:
    try:
        r = _session.get(_url(path), timeout=JEB_API_TIMEOUT)
        if r.status_code == 422:
            raise HTTPException(status_code=422, detail=r.json())
        if not r.ok:
            raise HTTPException(status_code=r.status_code, detail=r.text)
        return r.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Upstream JEB API error: {e}")
