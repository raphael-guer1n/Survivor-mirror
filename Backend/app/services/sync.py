import time
from datetime import datetime
import logging
from typing import Iterable, List, Dict, Optional
from app.db.connection import get_connection
from app.clients.jeb_api import get_page, get_one, UpstreamHTTPError

log = logging.getLogger(__name__)

def _execute_many(conn, sql: str, rows: Iterable[tuple]):
    rows = list(rows)
    if not rows:
        return
    cur = conn.cursor()
    try:
        cur.executemany(sql, rows)
        conn.commit()
    finally:
        cur.close()

def _execute(conn, sql: str, params: tuple):
    cur = conn.cursor()
    try:
        cur.execute(sql, params)
        conn.commit()
    finally:
        cur.close()

def _iter_pages(path: str, page_size: int = 200, params: Optional[Dict] = None) -> Iterable[List[Dict]]:
    params = dict(params or {})
    skip = 0
    while True:
        params.update({"skip": skip, "limit": page_size})
        page = get_page(path, params=params)
        if not page:
            break
        yield page
        skip += page_size

def _iter_items(path: str, page_size: int = 200, params: Optional[Dict] = None) -> Iterable[Dict]:
    for page in _iter_pages(path, page_size=page_size, params=params):
        for item in page:
            yield item
def _get_last_synced_id(conn, entity: str) -> int:
    cur = conn.cursor()
    try:
        cur.execute("SELECT last_id FROM sync_state WHERE entity=%s", (entity,))
        row = cur.fetchone()
        return row[0] if row else 0
    finally:
        cur.close()

def _set_last_synced_id(conn, entity: str, last_id: int):
    print(f"[DEBUG] _set_last_synced_id called for entity={entity}, last_id={last_id}")
    cur = conn.cursor()
    try:
        cur.execute("REPLACE INTO sync_state (entity, last_id) VALUES (%s, %s)", (entity, last_id))
        conn.commit()
        print(f"[DEBUG] sync_state updated: entity={entity}, last_id={last_id}")
    except Exception as e:
        print(f"[ERROR] Failed to update sync_state for entity={entity}: {e}")
    finally:
        cur.close()

def sync_startups():
    conn = get_connection()
    try:
        entity = "startups"
        last_id = _get_last_synced_id(conn, entity)
        ins_sql = """
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
        """
        batch = []
        max_id = last_id
        for it in _iter_items("/startups", page_size=200, params={"skip": last_id}):
            sid = it.get("id")
            if not sid or sid <= last_id:
                continue
            batch.append((
                sid,
                it.get("name"),
                it.get("legal_status"),
                it.get("address"),
                it.get("email"),
                it.get("phone"),
                it.get("sector"),
                it.get("maturity"),
            ))
            if sid > max_id:
                max_id = sid
            if len(batch) >= 500:
                _execute_many(conn, ins_sql, batch); batch.clear()
        _execute_many(conn, ins_sql, batch)
        if max_id > last_id:
            _set_last_synced_id(conn, entity, max_id)

        upd_detail_sql = """
        UPDATE startups
           SET created_at=%s,
               description=%s,
               website_url=%s,
               social_media_url=%s,
               project_status=%s,
               needs=%s
         WHERE id=%s
        """
        ins_founder_sql = """
        INSERT INTO founders (id, name, startup_id)
        VALUES (%s,%s,%s)
        ON DUPLICATE KEY UPDATE
          name=VALUES(name),
          startup_id=VALUES(startup_id)
        """

        for it in _iter_items("/startups", page_size=200, params={"skip": last_id}):
            sid = it.get("id")
            if not sid or sid <= last_id:
                continue
            try:
                detail = get_one(f"/startups/{sid}")
            except UpstreamHTTPError as e:
                log.warning(f"[sync_startups] detail KO id={sid}: {e}")
                continue
            if not detail:
                log.info(f"[sync_startups] detail 404 id={sid}, skip")
                continue

            _execute(conn, upd_detail_sql, (
                detail.get("created_at"),
                detail.get("description"),
                detail.get("website_url"),
                detail.get("social_media_url"),
                detail.get("project_status"),
                detail.get("needs"),
                sid
            ))

            _execute(conn, "DELETE FROM founders WHERE startup_id=%s", (sid,))
            founders = (detail.get("founders") or [])
            f_rows = []
            for f in founders:
                fid = f.get("id")
                if not fid:
                    continue
                f_rows.append((fid, f.get("name"), f.get("startup_id")))
            _execute_many(conn, ins_founder_sql, f_rows)

    finally:
        conn.close()

def sync_investors():
    conn = get_connection()
    try:
        entity = "investors"
        last_id = _get_last_synced_id(conn, entity)
        upsert_sql = """
        INSERT INTO investors (id, name, legal_status, address, email, phone, created_at, description, investor_type, investment_focus)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE
          name=VALUES(name),
          legal_status=VALUES(legal_status),
          address=VALUES(address),
          email=VALUES(email),
          phone=VALUES(phone),
          created_at=VALUES(created_at),
          description=VALUES(description),
          investor_type=VALUES(investor_type),
          investment_focus=VALUES(investment_focus)
        """
        batch = []
        max_id = last_id
        for it in _iter_items("/investors", page_size=300, params={"skip": last_id}):
            iid = it.get("id")
            if not iid or iid <= last_id:
                continue
            batch.append((
                iid,
                it.get("name"),
                it.get("legal_status"),
                it.get("address"),
                it.get("email"),
                it.get("phone"),
                it.get("created_at"),
                it.get("description"),
                it.get("investor_type"),
                it.get("investment_focus"),
            ))
            if iid > max_id:
                max_id = iid
            if len(batch) >= 500:
                _execute_many(conn, upsert_sql, batch); batch.clear()
        _execute_many(conn, upsert_sql, batch)
        if max_id > last_id:
            _set_last_synced_id(conn, entity, max_id)
    finally:
        conn.close()

def sync_partners():
    conn = get_connection()
    try:
        entity = "partners"
        last_id = _get_last_synced_id(conn, entity)
        upsert_sql = """
        INSERT INTO partners (id, name, legal_status, address, email, phone, created_at, description, partnership_type)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE
          name=VALUES(name),
          legal_status=VALUES(legal_status),
          address=VALUES(address),
          email=VALUES(email),
          phone=VALUES(phone),
          created_at=VALUES(created_at),
          description=VALUES(description),
          partnership_type=VALUES(partnership_type)
        """
        batch = []
        max_id = last_id
        for it in _iter_items("/partners", page_size=300, params={"skip": last_id}):
            pid = it.get("id")
            if not pid or pid <= last_id:
                continue
            batch.append((
                pid,
                it.get("name"),
                it.get("legal_status"),
                it.get("address"),
                it.get("email"),
                it.get("phone"),
                it.get("created_at"),
                it.get("description"),
                it.get("partnership_type"),
            ))
            if pid > max_id:
                max_id = pid
            if len(batch) >= 500:
                _execute_many(conn, upsert_sql, batch); batch.clear()
        _execute_many(conn, upsert_sql, batch)
        if max_id > last_id:
            _set_last_synced_id(conn, entity, max_id)
    finally:
        conn.close()

def sync_news():
    conn = get_connection()
    try:
        entity = "news"
        last_id = _get_last_synced_id(conn, entity)
        upsert_sql = """
        INSERT INTO news (id, news_date, location, title, category, startup_id, description)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE
          news_date=VALUES(news_date),
          location=VALUES(location),
          title=VALUES(title),
          category=VALUES(category),
          startup_id=VALUES(startup_id),
          description=VALUES(description)
        """

        max_id = last_id
        for it in _iter_items("/news", page_size=300, params={"skip": last_id}):
            nid = it.get("id")
            if not nid or nid <= last_id:
                continue
            try:
                detail = get_one(f"/news/{nid}")
            except UpstreamHTTPError as e:
                log.warning(f"[sync_news] detail KO id={nid}: {e}")
                continue
            if not detail:
                log.info(f"[sync_news] detail 404 id={nid}, skip")
                continue

            _execute(conn, upsert_sql, (
                detail.get("id"),
                detail.get("news_date"),
                detail.get("location"),
                detail.get("title"),
                detail.get("category"),
                detail.get("startup_id"),
                detail.get("description"),
            ))
            if nid > max_id:
                max_id = nid
        if max_id > last_id:
            _set_last_synced_id(conn, entity, max_id)
    finally:
        conn.close()

def sync_events():
    conn = get_connection()
    try:
        entity = "events"
        last_id = _get_last_synced_id(conn, entity)
        upsert_sql = """
        INSERT INTO events (id, name, dates, location, description, event_type, target_audience)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE
          name=VALUES(name),
          dates=VALUES(dates),
          location=VALUES(location),
          description=VALUES(description),
          event_type=VALUES(event_type),
          target_audience=VALUES(target_audience)
        """
        batch = []
        max_id = last_id
        for it in _iter_items("/events", page_size=300, params={"skip": last_id}):
            eid = it.get("id")
            if not eid or eid <= last_id:
                continue
            batch.append((
                eid,
                it.get("name"),
                it.get("dates"),
                it.get("location"),
                it.get("description"),
                it.get("event_type"),
                it.get("target_audience"),
            ))
            if eid > max_id:
                max_id = eid
            if len(batch) >= 500:
                _execute_many(conn, upsert_sql, batch); batch.clear()
        _execute_many(conn, upsert_sql, batch)
        if max_id > last_id:
            _set_last_synced_id(conn, entity, max_id)
    finally:
        conn.close()

def sync_users():
    conn = get_connection()
    try:
        entity = "users"
        upsert_sql = """
        INSERT INTO users (id, email, name, role, founder_id, investor_id)
        VALUES (%s,%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE
          email=VALUES(email),
          name=VALUES(name),
          role=VALUES(role),
          founder_id=VALUES(founder_id),
          investor_id=VALUES(investor_id)
        """
        items = get_page("/users")
        rows = []
        max_id = 0
        for it in items:
            uid = it.get("id")
            if not uid:
                continue
            rows.append((
                uid,
                it.get("email"),
                it.get("name"),
                it.get("role"),
                it.get("founder_id"),
                it.get("investor_id"),
            ))
            if uid > max_id:
                max_id = uid
            if len(rows) >= 500:
                _execute_many(conn, upsert_sql, rows); rows.clear()
        _execute_many(conn, upsert_sql, rows)
        if max_id > 0:
            _set_last_synced_id(conn, entity, max_id)
    finally:
        conn.close()

def sync_all():
    """
    Enchaîne la sync sur tous les datasets, sans limite, avec pagination.
    N'interrompt pas tout en cas d'erreur amont sur un item : log puis continue.
    """
    results = {}
    for name, fn in [
        ("startups", sync_startups),
        ("investors", sync_investors),
        ("partners",  sync_partners),
        ("news",      sync_news),
        ("events",    sync_events),
        ("users",     sync_users),
    ]:
        try:
            fn()
            results[name] = "ok"
        except UpstreamHTTPError as e:
            log.warning(f"[sync_all] upstream error in {name}: {e}")
            results[name] = f"upstream_error:{e}"
        except Exception as e:
            log.exception(f"[sync_all] unexpected error in {name}: {e}")
            results[name] = f"error:{e}"
    print({"status": results, "synced_at": datetime.utcnow().isoformat() + "Z"})
    return results
