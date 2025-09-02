from datetime import datetime
from app.db.connection import get_connection
from app.clients.jeb_api import get_page, get_one

def _execute_many(conn, sql, rows):
    if not rows:
        return
    cur = conn.cursor()
    try:
        cur.executemany(sql, rows)
        conn.commit()
    finally:
        cur.close()

def _execute(conn, sql, params):
    cur = conn.cursor()
    try:
        cur.execute(sql, params)
        conn.commit()
    finally:
        cur.close()

def sync_startups(limit=200):
    conn = get_connection()
    try:
        items = get_page("/startups", params={"skip": 0, "limit": limit})
        sql = """
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
        rows = []
        for it in items:
            rows.append((
                it.get("id"),
                it.get("name"),
                it.get("legal_status"),
                it.get("address"),
                it.get("email"),
                it.get("phone"),
                it.get("sector"),
                it.get("maturity"),
            ))
        _execute_many(conn, sql, rows)

        for it in items:
            sid = it.get("id")
            if sid is None:
                continue
            detail = get_one(f"/startups/{sid}")

            _execute(conn, """
                UPDATE startups SET
                  created_at = %s,
                  description = %s,
                  website_url = %s,
                  social_media_url = %s,
                  project_status = %s,
                  needs = %s
                WHERE id = %s
            """, (
                detail.get("created_at"),
                detail.get("description"),
                detail.get("website_url"),
                detail.get("social_media_url"),
                detail.get("project_status"),
                detail.get("needs"),
                sid
            ))

            _execute(conn, "DELETE FROM founders WHERE startup_id=%s", (sid,))
            founders = detail.get("founders", []) or []
            fsql = """
            INSERT INTO founders (id, name, startup_id)
            VALUES (%s,%s,%s)
            ON DUPLICATE KEY UPDATE
              name=VALUES(name),
              startup_id=VALUES(startup_id)
            """
            frows = [(f.get("id"), f.get("name"), f.get("startup_id")) for f in founders if f.get("id")]
            _execute_many(conn, fsql, frows)

    finally:
        conn.close()

def sync_investors(limit=500):
    conn = get_connection()
    try:
        items = get_page("/investors", params={"skip": 0, "limit": limit})
        sql = """
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
        rows = []
        for it in items:
            rows.append((
                it.get("id"), it.get("name"), it.get("legal_status"), it.get("address"),
                it.get("email"), it.get("phone"), it.get("created_at"),
                it.get("description"), it.get("investor_type"), it.get("investment_focus")
            ))
        _execute_many(conn, sql, rows)
    finally:
        conn.close()

def sync_partners(limit=500):
    conn = get_connection()
    try:
        items = get_page("/partners", params={"skip": 0, "limit": limit})
        sql = """
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
        rows = []
        for it in items:
            rows.append((
                it.get("id"), it.get("name"), it.get("legal_status"), it.get("address"),
                it.get("email"), it.get("phone"), it.get("created_at"),
                it.get("description"), it.get("partnership_type")
            ))
        _execute_many(conn, sql, rows)
    finally:
        conn.close()

def sync_news(limit=500):
    conn = get_connection()
    try:
        items = get_page("/news", params={"skip": 0, "limit": limit})
        for it in items:
            nid = it.get("id")
            if nid is None:
                continue
            detail = get_one(f"/news/{nid}")
            _execute(conn, """
                INSERT INTO news (id, news_date, location, title, category, startup_id, description)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
                ON DUPLICATE KEY UPDATE
                  news_date=VALUES(news_date),
                  location=VALUES(location),
                  title=VALUES(title),
                  category=VALUES(category),
                  startup_id=VALUES(startup_id),
                  description=VALUES(description)
            """, (
                detail.get("id"),
                detail.get("news_date"),
                detail.get("location"),
                detail.get("title"),
                detail.get("category"),
                detail.get("startup_id"),
                detail.get("description"),
            ))
    finally:
        conn.close()

def sync_events(limit=500):
    conn = get_connection()
    try:
        items = get_page("/events", params={"skip": 0, "limit": limit})
        sql = """
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
        rows = []
        for it in items:
            rows.append((
                it.get("id"), it.get("name"), it.get("dates"), it.get("location"),
                it.get("description"), it.get("event_type"), it.get("target_audience")
            ))
        _execute_many(conn, sql, rows)
    finally:
        conn.close()

def sync_users(limit=1000):
    conn = get_connection()
    try:
        items = get_page("/users")
        sql = """
        INSERT INTO users (id, email, name, role, founder_id, investor_id)
        VALUES (%s,%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE
          email=VALUES(email),
          name=VALUES(name),
          role=VALUES(role),
          founder_id=VALUES(founder_id),
          investor_id=VALUES(investor_id)
        """
        rows = []
        for it in items:
            rows.append((
                it.get("id"),
                it.get("email"),
                it.get("name"),
                it.get("role"),
                it.get("founder_id"),
                it.get("investor_id"),
            ))
        _execute_many(conn, sql, rows)
    finally:
        conn.close()

def sync_all():
    sync_startups()
    sync_investors()
    sync_partners()
    sync_news()
    sync_events()
    sync_users()
    return {"synced_at": datetime.utcnow().isoformat() + "Z"}
