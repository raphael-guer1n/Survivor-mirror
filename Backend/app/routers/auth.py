from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from app.db.connection import get_connection
from app.schemas.user import UserRegister, UserLogin, UserOut
from app.utils.security import hash_password, verify_password
from app.utils.jwt import create_access_token, decode_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return payload

def require_admin(user=Depends(get_current_user)):
    if user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
    return user

@router.post("/register")
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

        token = create_access_token({"sub": str(new_user_id), "role": user.role})
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {"id": new_user_id, "email": email, "name": user.name, "role": user.role}
        }
    finally:
        cursor.close()
        conn.close()


@router.post("/login")
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

        token = create_access_token({"sub": str(row["id"]), "role": row["role"]})
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {"id": row["id"], "email": row["email"], "name": row["name"], "role": row["role"]}
        }
    finally:
        cursor.close()
        conn.close()

@router.get("/me")
def get_me(user=Depends(get_current_user)):
    user_id = user.get("sub")
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, email, name, role FROM users WHERE id = %s", (user_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="User not found")
        return row
    finally:
        cursor.close()
        conn.close()
