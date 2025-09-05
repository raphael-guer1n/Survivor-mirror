from fastapi import APIRouter, HTTPException, Query, Depends
from app.db.connection import get_connection
from app.schemas.startup import StartupCreate, StartupUpdate, StartupOut, StartupDetail, FounderImage
from app.routers.auth import require_admin

router = APIRouter(prefix="/startups", tags=["startups"])

@router.get("/", response_model=list[StartupOut])
def get_startups(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id, name, legal_status, address, email, phone, sector, maturity, created_at,
                   description, website_url, social_media_url, project_status, needs
            FROM startups
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
            """,
            (limit, skip),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

@router.get("/{startup_id}", response_model=StartupDetail)
def get_startup(startup_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id, name, legal_status, address, email, phone, created_at,
                   description, website_url, social_media_url, project_status,
                   needs, sector, maturity
            FROM startups
            WHERE id = %s
            """,
            (startup_id,),
        )
        startup = cursor.fetchone()
        if not startup:
            raise HTTPException(status_code=404, detail="Startup not found")

        cursor.execute("SELECT id, name FROM founders WHERE startup_id = %s", (startup_id,))
        startup["founders"] = cursor.fetchall()
        return startup
    finally:
        cursor.close()
        conn.close()

@router.post("/", response_model=StartupOut)
def create_startup(startup: StartupCreate, admin=Depends(require_admin)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            INSERT INTO startups (name, legal_status, address, email, phone, sector, maturity,
                                  description, website_url, social_media_url, project_status, needs)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                startup.name, startup.legal_status, startup.address, startup.email, startup.phone,
                startup.sector, startup.maturity, startup.description, startup.website_url,
                startup.social_media_url, startup.project_status, startup.needs,
            ),
        )
        conn.commit()
        new_id = cursor.lastrowid
        cursor.execute("SELECT * FROM startups WHERE id = %s", (new_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

@router.put("/{startup_id}", response_model=StartupOut)
def update_startup(startup_id: int, startup: StartupUpdate, admin=Depends(require_admin)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id FROM startups WHERE id = %s", (startup_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Startup not found")

        fields = []
        values = []
        for field, value in startup.dict(exclude_unset=True).items():
            if value == 0:
                value = None
            fields.append(f"{field}=%s")
            values.append(value)

        if not fields:
            raise HTTPException(status_code=400, detail="No fields to update")

        values.append(startup_id)
        sql = f"UPDATE startups SET {', '.join(fields)} WHERE id = %s"
        cursor.execute(sql, tuple(values))
        conn.commit()

        cursor.execute("SELECT * FROM startups WHERE id = %s", (startup_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

@router.delete("/{startup_id}")
def delete_startup(startup_id: int, admin=Depends(require_admin)):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM startups WHERE id = %s", (startup_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Startup not found")

        cursor.execute("DELETE FROM startups WHERE id = %s", (startup_id,))
        conn.commit()
        return {"message": f"Startup {startup_id} deleted successfully"}
    finally:
        cursor.close()
        conn.close()

@router.get("/{startup_id}/founders/{founder_id}/image", response_model=FounderImage)
def get_founder_image(startup_id: int, founder_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT name FROM founders WHERE id = %s AND startup_id = %s",
            (founder_id, startup_id),
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Founder not found")
        return {"image_url": row["name"]}
    finally:
        cursor.close()
        conn.close()