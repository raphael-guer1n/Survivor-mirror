from pydantic import BaseModel
from typing import Optional

class FounderBase(BaseModel):
    name: str

class FounderOut(BaseModel):
    id: int
    name: str
    startup_id: Optional[int] = None
    image_s3_key: Optional[str] = None

    class Config:
        from_attributes = True
