from fastapi import APIRouter, HTTPException
from app.db.connection import get_connection
from app.schemas.user import UserRegister, UserLogin, UserOut
from app.utils.security import hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserOut)
def register(user: UserRegister):
    email = user.email.strip().lower()
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email already registered")

        password_hash = hash_password(user.password)
        cursor.execute(
            "INSERT INTO users (email, name, role, password_hash) VALUES (%s, %s, %s, %s)",
            (email, user.name, user.role, password_hash)
        )
        conn.commit()
        new_user_id = cursor.lastrowid

        return {"id": new_user_id, "email": email, "name": user.name, "role": user.role}
    finally:
        cursor.close()
        conn.close()

@router.post("/login", response_model=UserOut)
def login(credentials: UserLogin):
    email = credentials.email.strip().lower()
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT id, email, name, role, password_hash FROM users WHERE email = %s",
            (email,)
        )
        row = cursor.fetchone()
        if not row or not row.get("password_hash"):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        if not verify_password(credentials.password, row["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        return {"id": row["id"], "email": row["email"], "name": row["name"], "role": row["role"]}
    finally:
        cursor.close()
        conn.close()
