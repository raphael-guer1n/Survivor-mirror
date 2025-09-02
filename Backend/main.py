import mysql.connector
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import bcrypt

app = FastAPI()

def get_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        port=3327,
        user="admin",
        password="password",
        database="jeb_incubator"
    )

def hash_password(plain: str) -> str:
    hashed = bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt(rounds=12))
    return hashed.decode("utf-8")

def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False

class UserRegister(BaseModel):
    email: str
    name: str
    password: str
    role: str = "user"

class UserLogin(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    id: int
    email: str
    name: str
    role: str

@app.post("/register", response_model=UserOut)
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

@app.post("/login", response_model=UserOut)
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
