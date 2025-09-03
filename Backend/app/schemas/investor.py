from pydantic import BaseModel
from datetime import date

class Investor(BaseModel):
    id: int
    name: str
    legal_status: str | None = None
    address: str | None = None
    email: str
    phone: str | None = None
    created_at: date | None = None
    description: str | None = None
    investor_type: str | None = None
    investment_focus: str | None = None

    class Config:
        orm_mode = True


class InvestorImage(BaseModel):
    image_url: str