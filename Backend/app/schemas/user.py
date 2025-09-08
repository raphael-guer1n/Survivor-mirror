from pydantic import BaseModel
from typing import Optional

class UserRegister(BaseModel):
    email: str
    name: str
    password: str
    role: str = "user"

class UserLogin(BaseModel):
    email: str
    password: str

class UserCreate(BaseModel):
    email: str
    name: str
    role: str = "user"
    password: str
    founder_id: Optional[int] = None
    investor_id: Optional[int] = None
    image_s3_key: Optional[str] = None

class UserUpdate(BaseModel):
    email: Optional[str] = None
    name: Optional[str] = None
    role: Optional[str] = None
    founder_id: Optional[int] = None
    investor_id: Optional[int] = None
    image_s3_key: Optional[str] = None

class UserOut(BaseModel):
    id: int
    email: str
    name: str
    role: str
    founder_id: Optional[int] = None
    investor_id: Optional[int] = None
    image_s3_key: Optional[str] = None

    class Config:
        from_attributes = True
