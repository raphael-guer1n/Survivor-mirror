import requests
import io
import time
from typing import Any, Dict, List
from app.db.connection import get_connection
from app.utils.s3 import upload_file_to_s3
from app.core import config

API_BASE = config.JEB_API_BASE_URL
HEADERS = {"X-Group-Authorization": config.JEB_API_KEY}
REQUEST_TIMEOUT = config.JEB_API_TIMEOUT or 30

REQUEST_SLEEP = 0.005


class SyncService:
    def __init__(self, conn=None):
        self.conn = conn or get_connection()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.conn.close()

    def _fetch_json(self, url: str) -> Any:
        """Fetch JSON with retry for 429 and rate limit backoff."""
        while True:
            resp = requests.get(url, headers=HEADERS)
            if resp.status_code == 429:
                retry_after = int(resp.headers.get("Retry-After", "5"))
                print(f"[WARN] 429 Too Many Requests. Retrying after {retry_after}s")
                time.sleep(retry_after)
                continue
            resp.raise_for_status()
            time.sleep(REQUEST_SLEEP)
            return resp.json()

    def _fetch_and_upload_image(
        self, url: str, key_prefix: str, entity_id: int, table: str, cursor
    ):
        """Fetch image from JEB API and upload to S3."""
        img_resp = requests.get(url, headers=HEADERS, stream=True)
        time.sleep(REQUEST_SLEEP)
        if img_resp.status_code == 200 and img_resp.content:
            content_type = img_resp.headers.get("Content-Type", "image/jpeg")
            ext = content_type.split("/")[-1]
            key = f"{key_prefix}/{entity_id}/image.{ext}"
            upload_file_to_s3(io.BytesIO(img_resp.content), key, content_type)
            cursor.execute(
                f"UPDATE {table} SET image_s3_key=%s WHERE id=%s", (key, entity_id)
            )
            return key
        return None

    def _get_last_synced(self, entity: str, cursor) -> int:
        cursor.execute("SELECT last_id FROM sync_state WHERE entity=%s", (entity,))
        row = cursor.fetchone()
        return row["last_id"] if row else 0

    def _update_last_synced(self, entity: str, last_id: int, cursor):
        cursor.execute(
            """
            INSERT INTO sync_state (entity, last_id)
            VALUES (%s,%s)
            ON DUPLICATE KEY UPDATE last_id=VALUES(last_id)
            """,
            (entity, last_id),
        )

    def sync_startups(self, limit=20):
        cursor = self.conn.cursor(dictionary=True)
        try:
            last_id = self._get_last_synced("startups", cursor)
            startups = self._fetch_json(f"{API_BASE}/startups?skip={last_id}&limit={limit}")
            max_id = last_id
            for s in startups:
                cursor.execute(
                    """
                    INSERT INTO startups (id, name, legal_status, address, email, phone, sector, maturity)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                    ON DUPLICATE KEY UPDATE
                        name=VALUES(name),
                        legal_status=VALUES(legal_status),
                        address=VALUES(address),
                        email=VALUES(email),
                        phone=VALUES(phone),
                        sector=VALUES(sector),
                        maturity=VALUES(maturity)
                    """,
                    (
                        s["id"], s["name"], s.get("legal_status"), s.get("address"),
                        s["email"], s.get("phone"), s.get("sector"), s.get("maturity"),
                    ),
                )
                self._fetch_and_upload_image(
                    f"{API_BASE}/startups/{s['id']}/image",
                    "startups",
                    s["id"],
                    "startups",
                    cursor,
                )
                max_id = max(max_id, s["id"])
            if max_id > last_id:
                self._update_last_synced("startups", max_id, cursor)
            self.conn.commit()
        finally:
            cursor.close()

    def sync_investors(self, limit=20):
        cursor = self.conn.cursor(dictionary=True)
        try:
            last_id = self._get_last_synced("investors", cursor)
            investors = self._fetch_json(f"{API_BASE}/investors?skip={last_id}&limit={limit}")
            max_id = last_id
            for inv in investors:
                cursor.execute(
                    """
                    INSERT INTO investors (id, name, legal_status, address, email, phone, created_at, description, investor_type, investment_focus)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON DUPLICATE KEY UPDATE
                        name=VALUES(name),
                        legal_status=VALUES(legal_status),
                        address=VALUES(address),
                        phone=VALUES(phone),
                        description=VALUES(description),
                        investor_type=VALUES(investor_type),
                        investment_focus=VALUES(investment_focus)
                    """,
                    (
                        inv["id"], inv["name"], inv.get("legal_status"),
                        inv.get("address"), inv["email"], inv.get("phone"),
                        inv.get("created_at"), inv.get("description"),
                        inv.get("investor_type"), inv.get("investment_focus"),
                    ),
                )
                self._fetch_and_upload_image(
                    f"{API_BASE}/investors/{inv['id']}/image",
                    "investors",
                    inv["id"],
                    "investors",
                    cursor,
                )
                max_id = max(max_id, inv["id"])
            if max_id > last_id:
                self._update_last_synced("investors", max_id, cursor)
            self.conn.commit()
        finally:
            cursor.close()

    def sync_partners(self, limit=20):
        cursor = self.conn.cursor(dictionary=True)
        try:
            last_id = self._get_last_synced("partners", cursor)
            partners = self._fetch_json(f"{API_BASE}/partners?skip={last_id}&limit={limit}")
            max_id = last_id
            for p in partners:
                cursor.execute(
                    """
                    INSERT INTO partners (id, name, legal_status, address, email, phone,
                                          created_at, description, partnership_type)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON DUPLICATE KEY UPDATE
                        name=VALUES(name),
                        legal_status=VALUES(legal_status),
                        address=VALUES(address),
                        phone=VALUES(phone),
                        description=VALUES(description),
                        partnership_type=VALUES(partnership_type)
                    """,
                    (
                        p["id"], p["name"], p.get("legal_status"), p.get("address"),
                        p["email"], p.get("phone"), p.get("created_at"),
                        p.get("description"), p.get("partnership_type"),
                    ),
                )
                self._fetch_and_upload_image(
                    f"{API_BASE}/partners/{p['id']}/image",
                    "partners",
                    p["id"],
                    "partners",
                    cursor,
                )
                max_id = max(max_id, p["id"])
            if max_id > last_id:
                self._update_last_synced("partners", max_id, cursor)
            self.conn.commit()
        finally:
            cursor.close()

    def sync_news(self, limit=20):
        cursor = self.conn.cursor(dictionary=True)
        try:
            last_id = self._get_last_synced("news", cursor)
            news_list = self._fetch_json(f"{API_BASE}/news?skip={last_id}&limit={limit}")

            max_id = last_id
            for n in news_list:
                detail = self._fetch_json(f"{API_BASE}/news/{n['id']}")
                cursor.execute(
                    """
                    INSERT INTO news (id, title, news_date, location, category, startup_id, description)
                    VALUES (%s,%s,%s,%s,%s,%s,%s)
                    ON DUPLICATE KEY UPDATE
                        title=VALUES(title),
                        news_date=VALUES(news_date),
                        location=VALUES(location),
                        category=VALUES(category),
                        startup_id=VALUES(startup_id),
                        description=VALUES(description)
                    """,
                    (
                        detail["id"], detail["title"], detail.get("news_date"),
                        detail.get("location"), detail.get("category"),
                        detail.get("startup_id"), detail.get("description"),
                    ),
                )
                self._fetch_and_upload_image(
                    f"{API_BASE}/news/{n['id']}/image",
                    "news",
                    n["id"],
                    "news",
                    cursor,
                )
                max_id = max(max_id, n["id"])
            if max_id > last_id:
                self._update_last_synced("news", max_id, cursor)
            self.conn.commit()
        finally:
            cursor.close()

    def sync_events(self, limit=20):
        cursor = self.conn.cursor(dictionary=True)
        try:
            last_id = self._get_last_synced("events", cursor)
            events = self._fetch_json(f"{API_BASE}/events?skip={last_id}&limit={limit}")
            max_id = last_id
            for ev in events:
                cursor.execute(
                    """
                    INSERT INTO events (id, name, dates, location, description, event_type, target_audience)
                    VALUES (%s,%s,%s,%s,%s,%s,%s)
                    ON DUPLICATE KEY UPDATE
                        name=VALUES(name),
                        dates=VALUES(dates),
                        location=VALUES(location),
                        description=VALUES(description),
                        event_type=VALUES(event_type),
                        target_audience=VALUES(target_audience)
                    """,
                    (
                        ev["id"], ev["name"], ev.get("dates"), ev.get("location"),
                        ev.get("description"), ev.get("event_type"), ev.get("target_audience"),
                    ),
                )
                self._fetch_and_upload_image(
                    f"{API_BASE}/events/{ev['id']}/image",
                    "events",
                    ev["id"],
                    "events",
                    cursor,
                )
                max_id = max(max_id, ev["id"])
            if max_id > last_id:
                self._update_last_synced("events", max_id, cursor)
            self.conn.commit()
        finally:
            cursor.close()

    def sync_users(self, limit=20):
        cursor = self.conn.cursor(dictionary=True)
        try:
            last_id = self._get_last_synced("users", cursor)
            users = self._fetch_json(f"{API_BASE}/users?skip={last_id}&limit={limit}")
            max_id = last_id
            for u in users:
                cursor.execute(
                    """
                    INSERT INTO users (id, email, name, role, founder_id, investor_id)
                    VALUES (%s,%s,%s,%s,%s,%s)
                    ON DUPLICATE KEY UPDATE
                        name=VALUES(name),
                        role=VALUES(role),
                        founder_id=VALUES(founder_id),
                        investor_id=VALUES(investor_id)
                    """,
                    (
                        u["id"], u["email"], u["name"], u["role"],
                        u.get("founder_id"), u.get("investor_id"),
                    ),
                )
                self._fetch_and_upload_image(
                    f"{API_BASE}/users/{u['id']}/image",
                    "users",
                    u["id"],
                    "users",
                    cursor,
                )
                max_id = max(max_id, u["id"])
            if max_id > last_id:
                self._update_last_synced("users", max_id, cursor)
            self.conn.commit()
        finally:
            cursor.close()

def sync_all():
    with SyncService() as sync:
        sync.sync_startups()
        sync.sync_investors()
        sync.sync_partners()
        sync.sync_news()
        sync.sync_events()
        sync.sync_users()
