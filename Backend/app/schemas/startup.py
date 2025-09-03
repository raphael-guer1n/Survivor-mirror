from pydantic import BaseModel
from datetime import date

class Startup(BaseModel):
    id: int
    name: str
    legal_status: str | None = None
    address: str | None = None
    email: str
    phone: str | None = None
    sector: str | None = None
    maturity: str | None = None

    class Config:
        orm_mode = True


class Founder(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class StartupDetail(Startup):
    created_at: date | None = None
    description: str | None = None
    website_url: str | None = None
    social_media_url: str | None = None
    project_status: str | None = None
    needs: str | None = None
    founders: list[Founder] = []


class FounderImage(BaseModel):
    image_url: str