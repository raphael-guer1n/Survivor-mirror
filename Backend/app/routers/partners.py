from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from app.db.connection import get_connection
from app.schemas.partner import PartnerCreate, PartnerUpdate, PartnerOut, PartnerImage
from app.utils.s3 import upload_file_to_s3, generate_presigned_url

router = APIRouter(prefix="/partners", tags=["partners"])

@router.get("/", response_model=list[PartnerOut])
def get_partners(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id, name, legal_status, address, email, phone, created_at, description, partnership_type, image_s3_key
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
            SELECT id, name, legal_status, address, email, phone, created_at, description, partnership_type, image_s3_key
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
            INSERT INTO partners (name, legal_status, address, email, phone, description, partnership_type, image_s3_key)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                partner.name, partner.legal_status, partner.address, partner.email,
                partner.phone, partner.description, partner.partnership_type, partner.image_s3_key,
            ),
        )
        conn.commit()
        new_id = cursor.lastrowid
        cursor.execute(
            "SELECT id, name, legal_status, address, email, phone, created_at, description, partnership_type, image_s3_key FROM partners WHERE id = %s",
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
            "SELECT id, name, legal_status, address, email, phone, created_at, description, partnership_type, image_s3_key FROM partners WHERE id = %s",
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

@router.post("/{partner_id}/image", response_model=PartnerImage)
async def upload_partner_image(partner_id: int, file: UploadFile = File(...)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id FROM partners WHERE id = %s", (partner_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Partner not found")
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Invalid file type")
        key = f"partners/{partner_id}/{file.filename}"
        url = upload_file_to_s3(file.file, key, file.content_type)
        cursor.execute("UPDATE partners SET image_s3_key=%s WHERE id=%s", (key, partner_id))
        conn.commit()
        return {"image_url": url}
    finally:
        cursor.close()
        conn.close()

@router.get("/{partner_id}/image", response_model=PartnerImage)
def get_partner_image(partner_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT image_s3_key FROM partners WHERE id = %s", (partner_id,))
        row = cursor.fetchone()
        if not row or not row["image_s3_key"]:
            raise HTTPException(status_code=404, detail="Image not found")
        url = generate_presigned_url(row["image_s3_key"])
        return {"image_url": url}
    finally:
        cursor.close()
        conn.close()

@router.put("/{partner_id}/image", response_model=PartnerImage)
async def update_partner_image(partner_id: int, file: UploadFile = File(...)):
    return await upload_partner_image(partner_id, file)

@router.delete("/{partner_id}/image")
def delete_partner_image(partner_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT image_s3_key FROM partners WHERE id = %s", (partner_id,))
        row = cursor.fetchone()
        if not row or not row[0]:
            raise HTTPException(status_code=404, detail="Image not found")
        cursor.execute("UPDATE partners SET image_s3_key=NULL WHERE id=%s", (partner_id,))
        conn.commit()
        return {"message": f"Image for partner {partner_id} deleted successfully"}
    finally:
        cursor.close()
        conn.close()
