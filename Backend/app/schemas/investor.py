from pydantic import BaseModel
from typing import Optional
from datetime import date

class InvestorBase(BaseModel):
    name: str
    legal_status: Optional[str] = None
    address: Optional[str] = None
    email: str
    phone: Optional[str] = None
    investor_type: Optional[str] = None
    investment_focus: Optional[str] = None

class InvestorCreate(InvestorBase):
    description: Optional[str] = None

class InvestorUpdate(BaseModel):
    name: Optional[str] = None
    legal_status: Optional[str] = None
    address: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    investor_type: Optional[str] = None
    investment_focus: Optional[str] = None
    description: Optional[str] = None

class InvestorOut(InvestorBase):
    id: int
    created_at: Optional[date] = None
    description: Optional[str] = None

    class Config:
        orm_mode = True
