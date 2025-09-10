from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Depends
from app.db.connection import get_connection
from app.schemas.startup import StartupCreate, StartupUpdate, StartupOut, StartupDetail, FounderImage
from app.routers.auth import require_founder, require_founder_of_startup, get_user_name
from app.utils.s3 import upload_file_to_s3, generate_presigned_url

router = APIRouter(prefix="/startups", tags=["startups"])

@router.get("/", response_model=list[StartupOut])
def get_startups(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id, name, legal_status, address, email, phone, sector, maturity, created_at,
                   description, website_url, social_media_url, project_status, needs,
                   image_s3_key, view_count      -- 👈 include view_count here
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

@router.get("/most-viewed", response_model=list[StartupOut])
def get_most_viewed_startups(limit: int = Query(10, ge=1, le=100)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id, name, legal_status, address, email, phone, sector, maturity,
                   created_at, description, website_url, social_media_url,
                   project_status, needs, image_s3_key, view_count
            FROM startups
            ORDER BY view_count DESC
            LIMIT %s
            """,
            (limit,),
        )
        startups = cursor.fetchall()
        if not startups:
            raise HTTPException(status_code=404, detail="No startups found")
        return startups
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
                   needs, sector, maturity, image_s3_key, view_count   -- 👈 include it here
            FROM startups
            WHERE id = %s
            """,
            (startup_id,),
        )
        startup = cursor.fetchone()
        if not startup:
            raise HTTPException(status_code=404, detail="Startup not found")
        cursor.execute(
            "SELECT id, name, image_s3_key FROM founders WHERE startup_id = %s",
            (startup_id,),
        )
        startup["founders"] = cursor.fetchall()
        return startup
    finally:
        cursor.close()
        conn.close()

@router.post("/", response_model=StartupOut)
def create_startup(startup: StartupCreate, user=Depends(require_founder)):
    user_id = user.get("sub")
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id FROM startups WHERE email = %s", (startup.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=409, detail="A startup with this email already exists.")
        cursor.execute(
            """
            INSERT INTO startups (name, legal_status, address, email, phone, sector, maturity,
                                  description, website_url, social_media_url, project_status, needs, image_s3_key)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                startup.name, startup.legal_status, startup.address, startup.email, startup.phone,
                startup.sector, startup.maturity, startup.description, startup.website_url,
                startup.social_media_url, startup.project_status, startup.needs,
            ),
        )
        if user.get("role") != "admin":
            new_id = cursor.lastrowid
            user_name = get_user_name(user_id)
            cursor.execute(
                """
                INSERT INTO founders (name, startup_id) VALUES (%s, %s)
                """,
                (user_name, new_id)
            )
            new_founder_id = cursor.lastrowid
            cursor.execute(
                """
                UPDATE users SET founder_id = %s WHERE id = %s
                """,
                (new_founder_id, user_id)
            )
        conn.commit()
        cursor.execute("SELECT * FROM startups WHERE id = %s", (new_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

@router.put("/{startup_id}", response_model=StartupOut)
def update_startup(startup_id: int, startup: StartupUpdate, user=Depends(require_founder_of_startup)):
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
def delete_startup(startup_id: int, user=Depends(require_founder_of_startup)):
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

@router.post("/{startup_id}/image", response_model=FounderImage)
async def upload_startup_image(startup_id: int, file: UploadFile = File(...)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id FROM startups WHERE id = %s", (startup_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Startup not found")
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Invalid file type")
        key = f"startups/{startup_id}/{file.filename}"
        url = upload_file_to_s3(file.file, key, file.content_type)
        cursor.execute("UPDATE startups SET image_s3_key=%s WHERE id=%s", (key, startup_id))
        conn.commit()
        return {"image_url": url}
    finally:
        cursor.close()
        conn.close()

@router.get("/{startup_id}/image", response_model=FounderImage)
def get_startup_image(startup_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT image_s3_key FROM startups WHERE id = %s", (startup_id,))
        row = cursor.fetchone()
        if not row or not row["image_s3_key"]:
            raise HTTPException(status_code=404, detail="Image not found")
        url = generate_presigned_url(row["image_s3_key"])
        return {"image_url": url}
    finally:
        cursor.close()
        conn.close()

@router.put("/{startup_id}/image", response_model=FounderImage)
async def update_startup_image(startup_id: int, file: UploadFile = File(...)):
    return await upload_startup_image(startup_id, file)

@router.delete("/{startup_id}/image")
def delete_startup_image(startup_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT image_s3_key FROM startups WHERE id = %s", (startup_id,))
        row = cursor.fetchone()
        if not row or not row[0]:
            raise HTTPException(status_code=404, detail="Image not found")
        cursor.execute("UPDATE startups SET image_s3_key=NULL WHERE id=%s", (startup_id,))
        conn.commit()
        return {"message": f"Image for startup {startup_id} deleted successfully"}
    finally:
        cursor.close()
        conn.close()

@router.post("/{startup_id}/view")
def increment_startup_view(startup_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, view_count FROM startups WHERE id = %s", (startup_id,))
        startup = cursor.fetchone()
        if not startup:
            raise HTTPException(status_code=404, detail="Startup not found")
        cursor.execute(
            "UPDATE startups SET view_count = view_count + 1 WHERE id = %s", (startup_id,)
        )
        conn.commit()
        return {"startup_id": startup_id, "new_view_count": startup["view_count"] + 1}
    finally:
        cursor.close()
        conn.close()

@router.get("/{startup_id}/view")
def get_startup_view_count(startup_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, view_count FROM startups WHERE id = %s", (startup_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Startup not found")
        return {"startup_id": row["id"], "view_count": row["view_count"]}
    finally:
        cursor.close()
        conn.close()

@router.get("/views/total")
def get_total_startup_views():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT SUM(view_count) FROM startups")
        total = cursor.fetchone()[0] or 0
        return {"total_views": total}
    finally:
        cursor.close()
        conn.close()
