from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from app.db.connection import get_connection
from app.schemas.user import UserOut, UserCreate, UserUpdate
from app.utils.security import hash_password
from app.schemas.event import EventImage
from app.utils.s3 import upload_file_to_s3, generate_presigned_url
from app.routers.auth import require_admin, require_owner_of_user

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=list[UserOut])
def get_users(skip: int = 0, limit: int = 100, admin=Depends(require_admin)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id, email, name, role, founder_id, investor_id, image_s3_key
            FROM users
            LIMIT %s OFFSET %s
            """,
            (limit, skip),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, admin=Depends(require_admin)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id, email, name, role, founder_id, investor_id, image_s3_key
            FROM users
            WHERE id = %s
            """,
            (user_id,),
        )
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    finally:
        cursor.close()
        conn.close()

@router.get("/email/{email}", response_model=UserOut)
def get_user_by_email(email: str, admin=Depends(require_admin)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id, email, name, role, founder_id, investor_id, image_s3_key
            FROM users
            WHERE email = %s
            """,
            (email,),
        )
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    finally:
        cursor.close()
        conn.close()

@router.post("/", response_model=UserOut)
def create_user(user: UserCreate, admin=Depends(require_admin)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id FROM users WHERE email = %s", (user.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email already exists")
        password_hash = hash_password(user.password)
        cursor.execute(
            """
            INSERT INTO users (email, name, role, founder_id, investor_id, password_hash)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                user.email, user.name, user.role, user.founder_id if user.founder_id else None, user.investor_id if user.investor_id else None, password_hash,
            ),
        )
        conn.commit()
        new_id = cursor.lastrowid
        cursor.execute(
            "SELECT id, email, name, role, founder_id, investor_id FROM users WHERE id = %s", (new_id,),
        )
        return cursor.fetchone()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"DB error: {e}")
    finally:
        cursor.close()
        conn.close()

@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: int, user: UserUpdate, admin=Depends(require_owner_of_user)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="User not found")
        fields, values = [], []
        for field, value in user.dict(exclude_unset=True).items():
            if field in ("founder_id", "investor_id") and value == 0:
                value = None
            fields.append(f"{field}=%s")
            values.append(value)
        if not fields:
            raise HTTPException(status_code=400, detail="No fields to update")
        values.append(user_id)
        sql = f"UPDATE users SET {', '.join(fields)} WHERE id = %s"
        cursor.execute(sql, tuple(values))
        conn.commit()
        cursor.execute(
            """
            SELECT id, email, name, role, founder_id, investor_id, image_s3_key
            FROM users WHERE id = %s
            """,
            (user_id,),
        )
        return cursor.fetchone()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"DB error: {e}")
    finally:
        cursor.close()
        conn.close()

@router.delete("/{user_id}")
def delete_user(user_id: int, admin=Depends(require_admin)):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="User not found")
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        return {"message": f"User {user_id} deleted successfully"}
    finally:
        cursor.close()
        conn.close()

@router.post("/{user_id}/image", response_model=EventImage)
async def upload_user_image(user_id: int, file: UploadFile = File(...)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="User not found")
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Invalid file type")
        key = f"users/{user_id}/{file.filename}"
        url = upload_file_to_s3(file.file, key, file.content_type)
        cursor.execute("UPDATE users SET image_s3_key=%s WHERE id=%s", (key, user_id))
        conn.commit()
        return {"image_url": url}
    finally:
        cursor.close()
        conn.close()

@router.get("/{user_id}/image", response_model=EventImage)
def get_user_image(user_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT image_s3_key FROM users WHERE id = %s", (user_id,))
        row = cursor.fetchone()
        if not row or not row["image_s3_key"]:
            raise HTTPException(status_code=404, detail="Image not found")
        url = generate_presigned_url(row["image_s3_key"])
        return {"image_url": url}
    finally:
        cursor.close()
        conn.close()

@router.put("/{user_id}/image", response_model=EventImage)
async def update_user_image(user_id: int, file: UploadFile = File(...)):
    return await upload_user_image(user_id, file)

@router.delete("/{user_id}/image")
def delete_user_image(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT image_s3_key FROM users WHERE id = %s", (user_id,))
        row = cursor.fetchone()
        if not row or not row[0]:
            raise HTTPException(status_code=404, detail="Image not found")
        key = row[0]
        cursor.execute("UPDATE users SET image_s3_key=NULL WHERE id=%s", (user_id,))
        conn.commit()
        return {"message": f"Image for user {user_id} deleted successfully"}
    finally:
        cursor.close()
        conn.close()

@router.get("/{user_id}/startup")
def get_user_startup(user_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT founder_id FROM users WHERE id = %s",
            (user_id,)
        )
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        founder_id = user["founder_id"]
        if not founder_id:
            raise HTTPException(status_code=404, detail="User is not a founder or has no startup")
        cursor.execute(
            "SELECT startup_id FROM founders WHERE id = %s",
            (founder_id,)
        )
        founder = cursor.fetchone()
        if not founder or not founder["startup_id"]:
            raise HTTPException(status_code=404, detail="Startup not found for this user")
        return {"user_id": user_id, "startup_id": founder["startup_id"]}
    finally:
        cursor.close()
        conn.close()
