from pydantic import BaseModel
from typing import Optional, List
from datetime import date

class StartupBase(BaseModel):
    name: str
    legal_status: Optional[str] = None
    address: Optional[str] = None
    email: str
    phone: Optional[str] = None
    sector: Optional[str] = None
    maturity: Optional[str] = None

class StartupCreate(StartupBase):
    description: Optional[str] = None
    website_url: Optional[str] = None
    social_media_url: Optional[str] = None
    project_status: Optional[str] = None
    needs: Optional[str] = None

class StartupUpdate(BaseModel):
    name: Optional[str] = None
    legal_status: Optional[str] = None
    address: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    sector: Optional[str] = None
    maturity: Optional[str] = None
    description: Optional[str] = None
    website_url: Optional[str] = None
    social_media_url: Optional[str] = None
    project_status: Optional[str] = None
    needs: Optional[str] = None

class StartupOut(StartupBase):
    id: int
    created_at: Optional[date] = None
    description: Optional[str] = None
    website_url: Optional[str] = None
    social_media_url: Optional[str] = None
    project_status: Optional[str] = None
    needs: Optional[str] = None

    class Config:
        orm_mode = True

class Founder(BaseModel):
    id: int
    name: str

class StartupDetail(StartupOut):
    founders: List[Founder] = []

class FounderImage(BaseModel):
    image_url: str