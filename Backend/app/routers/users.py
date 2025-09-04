from fastapi import APIRouter, HTTPException
from app.db.connection import get_connection
from app.schemas.user import UserOut, UserCreate, UserUpdate
from app.utils.security import hash_password

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=list[UserOut])
def get_users(skip: int = 0, limit: int = 100):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, email, name, role FROM users LIMIT %s OFFSET %s", (limit, skip))
        users = cursor.fetchall()
        return users
    finally:
        cursor.close()
        conn.close()

@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, email, name, role FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    finally:
        cursor.close()
        conn.close()

@router.get("/email/{email}", response_model=UserOut)
def get_user_by_email(email: str):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, email, name, role FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    finally:
        cursor.close()
        conn.close()

@router.post("/", response_model=UserOut)
def create_user(user: UserCreate):
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

from fastapi import APIRouter, HTTPException
from app.db.connection import get_connection
from app.schemas.user import UserUpdate, UserOut

router = APIRouter(prefix="/users", tags=["users"])

@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: int, user: UserUpdate):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="User not found")

        fields = []
        values = []
        for field, value in user.dict(exclude_unset=True).items():
            # convert 0 → None for FKs
            if field in ("founder_id", "investor_id") and (value == 0):
                value = None
            fields.append(f"{field}=%s")
            values.append(value)

        if not fields:
            raise HTTPException(status_code=400, detail="No fields to update")

        values.append(user_id)
        sql = f"UPDATE users SET {', '.join(fields)} WHERE id = %s"
        cursor.execute(sql, tuple(values))
        conn.commit()

        cursor.execute("SELECT id, email, name, role, founder_id, investor_id FROM users WHERE id = %s", (user_id,))
        return cursor.fetchone()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"DB error: {e}")
    finally:
        cursor.close()
        conn.close()

@router.delete("/{user_id}")
def delete_user(user_id: int):
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