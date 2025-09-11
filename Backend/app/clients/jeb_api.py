import time
import requests
import logging
from typing import Optional
from app.core.config import JEB_API_BASE_URL, JEB_API_KEY, JEB_API_TIMEOUT

class UpstreamHTTPError(Exception):
    def __init__(self, status: int, text: str):
        super().__init__(f"Upstream HTTP {status}: {text[:200]}")
        self.status = status
        self.text = text

_session = requests.Session()
_session.headers.update({"X-Group-Authorization": JEB_API_KEY})

def _url(path: str) -> str:
    return f"{JEB_API_BASE_URL.rstrip('/')}/{path.lstrip('/')}"

def _request_with_retry(method: str, path: str, *,
                        params: Optional[dict] = None,
                        stream: bool = False,
                        retries: int = 2,
                        backoff: float = 0.5):

    url = _url(path)
    last_exc = None
    for attempt in range(retries + 1):
        try:
            resp = _session.request(method, url, params=params, timeout=JEB_API_TIMEOUT, stream=stream)
            if resp.status_code == 404:
                return resp
            if resp.status_code == 429:
                logging.warning(f"429 Too Many Requests on endpoint: {path} (attempt {attempt+1})")
            if 500 <= resp.status_code < 600:
                last_exc = UpstreamHTTPError(resp.status_code, resp.text)
                if attempt < retries:
                    time.sleep(backoff * (2 ** attempt))
                    continue
                raise last_exc
            if not resp.ok:
                raise UpstreamHTTPError(resp.status_code, resp.text)
            return resp
        except requests.RequestException as e:
            last_exc = e
            if attempt < retries:
                time.sleep(backoff * (2 ** attempt))
                continue
            raise e
    raise last_exc or RuntimeError("Unknown upstream error")

def get_page(path: str, params: dict | None = None) -> list[dict]:
    r = _request_with_retry("GET", path, params=params)
    if r.status_code == 404:
        return []
    data = r.json()
    return data if isinstance(data, list) else [data]

def get_one(path: str) -> dict | None:
    r = _request_with_retry("GET", path)
    if r.status_code == 404:
        return None
    return r.json()

def get_stream(path: str, params: dict | None = None):
    return _request_with_retry("GET", path, params=params, stream=True)
