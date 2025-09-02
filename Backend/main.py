import mysql.connector
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

def get_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        port=3327,
        user="admin",
        password="password",
        database="jeb_incubator"
    )

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
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id FROM users WHERE email = %s", (user.email,))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        raise HTTPException(status_code=400, detail="Email already registered")

    cursor.execute(
        "INSERT INTO users (email, name, role, password_hash) VALUES (%s, %s, %s, %s)",
        (user.email, user.name, user.role, user.password)  
    )
    conn.commit()
    new_user_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return {"id": new_user_id, "email": user.email, "name": user.name, "role": user.role}

@app.post("/login", response_model=UserOut)
def login(credentials: UserLogin):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT id, email, name, role, password_hash FROM users WHERE email = %s",
        (credentials.email,)
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if not row:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if credentials.password != row["password_hash"]:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {"id": row["id"], "email": row["email"], "name": row["name"], "role": row["role"]}
