from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Depends
from app.db.connection import get_connection
from app.schemas.founder import FounderOut
from app.utils.s3 import generate_presigned_url
from app.schemas.partner import PartnerImage

router = APIRouter(prefix="/founders", tags=["founders"])

@router.get("/{founder_id}/image", response_model=PartnerImage)
def get_founder_image(founder_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT image_s3_key FROM founders WHERE id = %s", (founder_id,))
        row = cursor.fetchone()
        if not row or not row["image_s3_key"]:
            raise HTTPException(status_code=404, detail="Image not found")
        url = generate_presigned_url(row["image_s3_key"])
        return {"image_url": url}
    finally:
        cursor.close()
        conn.close()
