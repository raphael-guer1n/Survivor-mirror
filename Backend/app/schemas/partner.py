from pydantic import BaseModel
from datetime import date

class Partner(BaseModel):
    id: int
    name: str
    legal_status: str | None = None
    address: str | None = None
    email: str
    phone: str | None = None
    created_at: date | None = None
    description: str | None = None
    partnership_type: str | None = None

    class Config:
        orm_mode = True