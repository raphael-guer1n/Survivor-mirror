from pydantic import BaseModel
from datetime import date

class News(BaseModel):
    id: int
    title: str
    news_date: date | None = None
    location: str | None = None
    category: str | None = None
    startup_id: int | None = None

    class Config:
        orm_mode = True


class NewsDetail(News):
    description: str | None = None


class NewsImage(BaseModel):
    image_url: str