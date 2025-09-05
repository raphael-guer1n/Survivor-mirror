from pydantic import BaseModel
from typing import Optional
from datetime import date

class NewsBase(BaseModel):
    title: str
    news_date: Optional[date] = None
    location: Optional[str] = None
    category: Optional[str] = None
    startup_id: Optional[int] = None

class NewsCreate(NewsBase):
    description: Optional[str] = None
    image_s3_key: Optional[str] = None  

class NewsUpdate(BaseModel):
    title: Optional[str] = None
    news_date: Optional[date] = None
    location: Optional[str] = None
    category: Optional[str] = None
    startup_id: Optional[int] = None
    description: Optional[str] = None
    image_s3_key: Optional[str] = None

class NewsOut(NewsBase):
    id: int
    description: Optional[str] = None
    image_s3_key: Optional[str] = None

    class Config:
        from_attributes = True
