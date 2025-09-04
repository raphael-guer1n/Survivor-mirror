from fastapi import APIRouter, HTTPException, Query
from app.db.connection import get_connection
from app.schemas.partner import PartnerCreate, PartnerUpdate, PartnerOut

router = APIRouter(prefix="/partners", tags=["partners"])

@router.get("/", response_model=list[PartnerOut])
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
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

@router.get("/{partner_id}", response_model=PartnerOut)
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
        partner = cursor.fetchone()
        if not partner:
            raise HTTPException(status_code=404, detail="Partner not found")
        return partner
    finally:
        cursor.close()
        conn.close()

@router.post("/", response_model=PartnerOut)
def create_partner(partner: PartnerCreate):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id FROM partners WHERE email = %s", (partner.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email already exists")

        cursor.execute(
            """
            INSERT INTO partners (name, legal_status, address, email, phone, description, partnership_type)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                partner.name, partner.legal_status, partner.address, partner.email,
                partner.phone, partner.description, partner.partnership_type,
            ),
        )
        conn.commit()
        new_id = cursor.lastrowid
        cursor.execute(
            "SELECT id, name, legal_status, address, email, phone, created_at, description, partnership_type FROM partners WHERE id = %s",
            (new_id,),
        )
        return cursor.fetchone()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"DB error: {e}")
    finally:
        cursor.close()
        conn.close()

@router.put("/{partner_id}", response_model=PartnerOut)
def update_partner(partner_id: int, partner: PartnerUpdate):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id FROM partners WHERE id = %s", (partner_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Partner not found")

        fields = []
        values = []
        for field, value in partner.dict(exclude_unset=True).items():
            if value == 0:
                value = None
            fields.append(f"{field}=%s")
            values.append(value)

        if not fields:
            raise HTTPException(status_code=400, detail="No fields to update")

        values.append(partner_id)
        sql = f"UPDATE partners SET {', '.join(fields)} WHERE id = %s"
        cursor.execute(sql, tuple(values))
        conn.commit()

        cursor.execute(
            "SELECT id, name, legal_status, address, email, phone, created_at, description, partnership_type FROM partners WHERE id = %s",
            (partner_id,),
        )
        return cursor.fetchone()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"DB error: {e}")
    finally:
        cursor.close()
        conn.close()

@router.delete("/{partner_id}")
def delete_partner(partner_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM partners WHERE id = %s", (partner_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Partner not found")

        cursor.execute("DELETE FROM partners WHERE id = %s", (partner_id,))
        conn.commit()
        return {"message": f"Partner {partner_id} deleted successfully"}
    finally:
        cursor.close()
        conn.close()