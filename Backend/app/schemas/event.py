from pydantic import BaseModel
from typing import Optional


class EventBase(BaseModel):
    name: str
    dates: str
    location: str
    description: str
    event_type: str
    target_audience: str


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    name: Optional[str] = None
    dates: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    event_type: Optional[str] = None
    target_audience: Optional[str] = None


class EventOut(EventBase):
    id: int

    class Config:
        orm_mode = True


class EventImage(BaseModel):
    image_url: str