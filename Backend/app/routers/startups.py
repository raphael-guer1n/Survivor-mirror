from fastapi import APIRouter, HTTPException, Query
from app.db.connection import get_connection
from app.schemas.startup import Startup, StartupDetail, Founder, FounderImage

router = APIRouter(prefix="/startups", tags=["startups"])

@router.get("/", response_model=list[Startup])
def get_startups(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id, name, legal_status, address, email, phone, sector, maturity
            FROM startups
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
            """,
            (limit, skip),
        )
        rows = cursor.fetchall()
        return rows
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
        cursor.execute(
            "SELECT id, name FROM founders WHERE startup_id = %s", (startup_id,)
        )
        founders = cursor.fetchall()
        startup["founders"] = founders

        return startup
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
