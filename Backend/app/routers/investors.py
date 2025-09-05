from fastapi import APIRouter, HTTPException, Query, Depends
from app.db.connection import get_connection
from app.schemas.investor import InvestorCreate, InvestorUpdate, InvestorOut
from app.routers.auth import require_admin

router = APIRouter(prefix="/investors", tags=["investors"])

@router.get("/", response_model=list[InvestorOut])
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
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

@router.get("/{investor_id}", response_model=InvestorOut)
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
        investor = cursor.fetchone()
        if not investor:
            raise HTTPException(status_code=404, detail="Investor not found")
        return investor
    finally:
        cursor.close()
        conn.close()

@router.post("/", response_model=InvestorOut)
def create_investor(investor: InvestorCreate, admin=Depends(require_admin)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id FROM investors WHERE email = %s", (investor.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email already exists")

        cursor.execute(
            """
            INSERT INTO investors (name, legal_status, address, email, phone, description, investor_type, investment_focus)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                investor.name, investor.legal_status, investor.address, investor.email,
                investor.phone, investor.description, investor.investor_type, investor.investment_focus,
            ),
        )
        conn.commit()
        new_id = cursor.lastrowid
        cursor.execute(
            "SELECT id, name, legal_status, address, email, phone, created_at, description, investor_type, investment_focus FROM investors WHERE id = %s",
            (new_id,),
        )
        return cursor.fetchone()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"DB error: {e}")
    finally:
        cursor.close()
        conn.close()

@router.put("/{investor_id}", response_model=InvestorOut)
def update_investor(investor_id: int, investor: InvestorUpdate, admin=Depends(require_admin)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id FROM investors WHERE id = %s", (investor_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Investor not found")

        fields = []
        values = []
        for field, value in investor.dict(exclude_unset=True).items():
            if value == 0:
                value = None
            fields.append(f"{field}=%s")
            values.append(value)

        if not fields:
            raise HTTPException(status_code=400, detail="No fields to update")

        values.append(investor_id)
        sql = f"UPDATE investors SET {', '.join(fields)} WHERE id = %s"
        cursor.execute(sql, tuple(values))
        conn.commit()

        cursor.execute(
            "SELECT id, name, legal_status, address, email, phone, created_at, description, investor_type, investment_focus FROM investors WHERE id = %s",
            (investor_id,),
        )
        return cursor.fetchone()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"DB error: {e}")
    finally:
        cursor.close()
        conn.close()

@router.delete("/{investor_id}")
def delete_investor(investor_id: int, admin=Depends(require_admin)):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM investors WHERE id = %s", (investor_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Investor not found")

        cursor.execute("DELETE FROM investors WHERE id = %s", (investor_id,))
        conn.commit()
        return {"message": f"Investor {investor_id} deleted successfully"}
    finally:
        cursor.close()
        conn.close()
