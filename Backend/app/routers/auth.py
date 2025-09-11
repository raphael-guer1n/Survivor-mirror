from fastapi import APIRouter, HTTPException, Depends, status, Response
from fastapi.security import OAuth2PasswordBearer
from app.db.connection import get_connection
from app.schemas.user import UserRegister, UserLogin, UserOut
from app.utils.security import hash_password, verify_password
from app.utils.jwt import create_access_token, decode_access_token
import random
from datetime import datetime, timedelta
from app.utils.email import send_verification_email
from app.schemas.email_verification import EmailRequest, CodeVerificationRequest, CompleteRegisterRequest, DefaultResponse, VerifyRegisterCodeResponse, CompleteRegisterResponse
from app.core.config import REGISTER_CODE_EXPIRES_MINUTES

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post(
        "/request-register",
        response_model=DefaultResponse,
        responses={
            200: {"model": DefaultResponse, "description": "Code sent"},
            409: {"model": DefaultResponse, "description": "Email already used"},
            },
)
def request_register(data: EmailRequest, response: Response):
    email = data.email.strip().lower()
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, password_hash, name, role FROM users WHERE email = %s", (email,),)
        user = cursor.fetchone()

        if user and user["password_hash"]:
            response.status_code = status.HTTP_409_CONFLICT
            return DefaultResponse(detail="Email already used, please login.",)

        code = str(random.randint(100000, 999999))
        now = datetime.utcnow()
        cursor.execute("DELETE FROM email_verifications WHERE email = %s", (email,))
        cursor.execute("INSERT INTO email_verifications (email, code, created_at) VALUES (%s, %s, %s)", (email, code, now),)
        conn.commit()

        send_verification_email(email, code)

        response.status_code = status.HTTP_200_OK
        return DefaultResponse(detail=f"Code sent to {email}, check your emails",)

    finally:
        cursor.close()
        conn.close()

@router.post(
        "/verify-register-code",
        response_model = VerifyRegisterCodeResponse,
        responses={
            200: {"model": VerifyRegisterCodeResponse, "description": "Code is valid"},
            401: {"model": VerifyRegisterCodeResponse, "description": "Wrong code or code expired"}
            },
)
def verify_register_code(data: CodeVerificationRequest, response: Response):
    email = data.email.strip().lower()
    code = data.code.strip()
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT code, created_at FROM email_verifications WHERE email = %s", (email,))
        row = cursor.fetchone()
        if not row or row["code"] != code:
            return VerifyRegisterCodeResponse(pre_fill = None, detail = "Wrong code")

        created_at = row["created_at"]
        if (datetime.utcnow() - created_at) > timedelta(minutes=int(REGISTER_CODE_EXPIRES_MINUTES)):
            return VerifyRegisterCodeResponse(pre_fill = None, detail = "Code expired")

        cursor.execute("SELECT id, name, role FROM users WHERE email = %s AND password_hash IS NULL", (email,))
        user = cursor.fetchone()
        if user:
            return VerifyRegisterCodeResponse(pre_fill={"name": user["name"], "role": user["role"]}, detail="Code valid, pre-filled user informations")
        else:
            return VerifyRegisterCodeResponse(pre_fill = None, detail="Code valid, could not pre-fill user informations")
    finally:
        cursor.close()
        conn.close()

@router.post(
    "/complete-register",
    response_model=CompleteRegisterResponse,
    responses={
        200: {"model": CompleteRegisterResponse, "description": "Registration complete"},
        400: {"model": CompleteRegisterResponse, "description": "Bad request"},
    },
)
def complete_register(data: CompleteRegisterRequest, response: Response):
    email = data.email.strip().lower()
    code = data.code.strip()
    name = data.name
    password = data.password
    role = data.role
    missing = []
    if not password:
        missing.append("password")
    if not name:
        missing.append("name")
    if not role:
        missing.append("role")
    if missing:
        response.status_code = status.HTTP_400_BAD_REQUEST
        missing_str = ", ".join(missing)
        return CompleteRegisterResponse(
            access_token=None,
            token_type=None,
            user=None,
            detail=f"Missing required field(s): {missing_str}."
        )
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT code, created_at FROM email_verifications WHERE email = %s", (email,))
        row = cursor.fetchone()
        if not row or row["code"] != code:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return CompleteRegisterResponse(
                access_token=None,
                token_type=None,
                user=None,
                detail="Wrong code."
            )
        if (datetime.utcnow() - row["created_at"]) > timedelta(minutes=10):
            response.status_code = status.HTTP_400_BAD_REQUEST
            return CompleteRegisterResponse(
                access_token=None,
                token_type=None,
                user=None,
                detail="Code expired"
            )

        password_hash = hash_password(password)
        cursor.execute("SELECT id FROM users WHERE email = %s AND password_hash IS NULL", (email,))
        user = cursor.fetchone()
        if user:
            cursor.execute("UPDATE users SET name = %s, role = %s, password_hash = %s WHERE email = %s", (name, role, password_hash, email))
            user_id = user["id"]
        else:
            cursor.execute("INSERT INTO users (email, name, role, password_hash) VALUES (%s, %s, %s, %s)", (email, name, role, password_hash))
            user_id = cursor.lastrowid
        conn.commit()
        cursor.execute("DELETE FROM email_verifications WHERE email = %s", (email,))
        conn.commit()
        token = create_access_token({"sub": str(user_id), "role": role})
        response.status_code = status.HTTP_200_OK
        return CompleteRegisterResponse(
            access_token=token,
            token_type="bearer",
            user={"id": user_id, "email": email, "name": name, "role": role},
            detail="Registration complete."
        )
    finally:
        cursor.close()
        conn.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return payload

def require_admin(user=Depends(get_current_user)):
    if user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="permission denied")
    return user

def require_founder(user=Depends(get_current_user)):
    role = user.get("role")
    if role != "founder" and role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="permission denied")
    return user

def require_founder_of_startup(startup_id, user=Depends(get_current_user)):
    if user.get("role") == "admin":
        return user
    if user.get("role") != "founder":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="permission denied")

    user_id = user.get("sub")
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT founder_id FROM users WHERE id = %s", (user_id,))
        row = cursor.fetchone()
        if not row or not row["founder_id"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="permission denied")
        founder_id = row["founder_id"]

        cursor.execute("SELECT id FROM founders WHERE id = %s AND startup_id = %s", (founder_id, startup_id))
        link = cursor.fetchone()
        if not link:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="permission denied: not founder of this startup")
        return user
    finally:
        cursor.close()
        conn.close()

def get_user_name(user_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name FROM users WHERE id = %s", (user_id,))
        user_row = cursor.fetchone()
        if not user_row:
            raise HTTPException(status_code=404, detail="User not found")
        return user_row["name"]

def require_investor(user=Depends(get_current_user)):
    role = user.get("role")
    if role != "investor" and role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="permission denied")
    return user


def require_investor_of_investor(investor_id, user=Depends(get_current_user)):
    if user.get("role") == "admin":
        return user
    if user.get("role") != "investor":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="permission denied")

    user_id = user.get("sub")
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT investor_id FROM users WHERE id = %s", (user_id,))
        row = cursor.fetchone()
        if not row or not row["investor_id"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="permission denied")
        user_investor_id = row["investor_id"]
        if int(user_investor_id) != int(investor_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="permission denied: not this investor")
        return user
    finally:
        cursor.close()
        conn.close()

def require_owner_of_user(user_id, user=Depends(get_current_user)):
    if user.get("role") == "admin":
        return user
    if user_id != user.get("sub"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="permission denied")

def check_founder_of_startup(user, startup_id):
    if user.get("role") == "admin":
        return
    if user.get("role") != "founder":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="permission denied")
    user_id = user.get("sub")
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT founder_id FROM users WHERE id = %s", (user_id,))
        row = cursor.fetchone()
        if not row or not row["founder_id"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="permission denied")
        founder_id = row["founder_id"]
        cursor.execute("SELECT id FROM founders WHERE id = %s AND startup_id = %s", (founder_id, startup_id))
        link = cursor.fetchone()
        if not link:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="permission denied: not founder of this startup")
    finally:
        cursor.close()
        conn.close()

@router.post("/register")
def register(user: UserRegister):
    email = user.email.strip().lower()

    if user.role not in ["founder", "investor"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid role. Only 'founder' or 'investor' are allowed."
        )
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email already registered")
        password_hash = hash_password(user.password)
        cursor.execute(
            """
            INSERT INTO users (email, name, role, password_hash)
            VALUES (%s, %s, %s, %s)
            """,
            (email, user.name, user.role, password_hash)
        )
        conn.commit()
        new_user_id = cursor.lastrowid
        token = create_access_token({"sub": str(new_user_id), "role": user.role})
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": new_user_id,
                "email": email,
                "name": user.name,
                "role": user.role
            }
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
            "SELECT id, email, name, role, password_hash FROM users WHERE email = %s", (email,))
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

@router.get("/me", response_model=UserOut)
def get_me(user=Depends(get_current_user)):
    user_id = user.get("sub")
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id, email, name, role, founder_id, investor_id, image_s3_key
            FROM users WHERE id = %s
            """,
            (user_id,),
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="User not found")
        return row
    finally:
        cursor.close()
        conn.close()
