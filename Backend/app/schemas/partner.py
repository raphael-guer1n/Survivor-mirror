from pydantic import BaseModel
from typing import Optional
from datetime import date

class PartnerBase(BaseModel):
    name: str
    legal_status: Optional[str] = None
    address: Optional[str] = None
    email: str
    phone: Optional[str] = None
    partnership_type: Optional[str] = None

class PartnerCreate(PartnerBase):
    description: Optional[str] = None

class PartnerUpdate(BaseModel):
    name: Optional[str] = None
    legal_status: Optional[str] = None
    address: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    partnership_type: Optional[str] = None
    description: Optional[str] = None

class PartnerOut(PartnerBase):
    id: int
    created_at: Optional[date] = None
    description: Optional[str] = None

    class Config:
        orm_mode = True
