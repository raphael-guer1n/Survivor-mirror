from fastapi import APIRouter, HTTPException, Query
from app.db.connection import get_connection
from app.schemas.partner import Partner

router = APIRouter(prefix="/partners", tags=["partners"])

@router.get("/", response_model=list[Partner])
def get_partners(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id, name, legal_status, address, email, phone, created_at, description, partnership_type
            FROM partners
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

@router.get("/{partner_id}", response_model=Partner)
def get_partner(partner_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id, name, legal_status, address, email, phone, created_at, description, partnership_type
            FROM partners
            WHERE id = %s
            """,
            (partner_id,),
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Partner not found")
        return row
    finally:
        cursor.close()
        conn.close()
