from fastapi import APIRouter, HTTPException, Query
from app.db.connection import get_connection
from app.schemas.investor import Investor, InvestorImage

router = APIRouter(prefix="/investors", tags=["investors"])

@router.get("/", response_model=list[Investor])
def get_investors(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id, name, legal_status, address, email, phone, created_at, description, investor_type, investment_focus
            FROM investors
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

@router.get("/{investor_id}", response_model=Investor)
def get_investor(investor_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id, name, legal_status, address, email, phone, created_at, description, investor_type, investment_focus
            FROM investors
            WHERE id = %s
            """,
            (investor_id,),
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Investor not found")
        return row
    finally:
        cursor.close()
        conn.close()

@router.get("/{investor_id}/image", response_model=InvestorImage)
def get_investor_image(investor_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT description FROM investors WHERE id = %s", (investor_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Investor not found")
        return {"image_url": row["description"]}
    finally:
        cursor.close()
        conn.close()
