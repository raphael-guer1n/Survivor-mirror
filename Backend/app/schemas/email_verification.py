from pydantic import BaseModel
from typing import Optional
from app.schemas.user import UserOut

class EmailRequest(BaseModel):
    email: str

class CodeVerificationRequest(BaseModel):
    email: str
    code: str

class CompleteRegisterRequest(BaseModel):
    email: str
    code: str
    name: str = None
    password: str = None
    role: str = "user"

class DefaultResponse(BaseModel):
    detail: str

class PreFillData(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None

class VerifyRegisterCodeResponse(BaseModel):
    pre_fill: Optional[PreFillData] = None
    detail: str

class CompleteRegisterResponse(BaseModel):
    access_token: Optional[str]
    token_type: Optional[str]
    user: Optional[UserOut] = None
    detail: Optional[str] = None