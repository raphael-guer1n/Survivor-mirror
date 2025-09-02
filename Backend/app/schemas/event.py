from pydantic import BaseModel

class Event(BaseModel):
    name: str
    dates: str
    location: str
    description: str
    event_type: str
    target_audience: str
    id: int

class EventImage(BaseModel):
    image_url: str