from fastapi import APIRouter, HTTPException, Query
from app.db.connection import get_connection
from app.schemas.news import News, NewsDetail, NewsImage

router = APIRouter(prefix="/news", tags=["news"])


@router.get("/", response_model=list[News])
def get_news(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1)):
    """
    Fetch all news items from the database.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id, title, news_date, location, category, startup_id
            FROM news
            ORDER BY news_date DESC
            LIMIT %s OFFSET %s
            """,
            (limit, skip),
        )
        rows = cursor.fetchall()
        return rows
    finally:
        cursor.close()
        conn.close()


@router.get("/{news_id}", response_model=NewsDetail)
def get_news_item(news_id: int):
    """
    Fetch a specific news item by ID from the database.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id, title, news_date, location, category, startup_id, description
            FROM news
            WHERE id = %s
            """,
            (news_id,),
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="News item not found")
        return row
    finally:
        cursor.close()
        conn.close()


@router.get("/{news_id}/image", response_model=NewsImage)
def get_news_image(news_id: int):
    """
    Fetch the image URL for a specific news item.
    ⚠️ Replace `description` with the actual column if you store image URLs elsewhere.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT description FROM news WHERE id = %s", (news_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="News item not found")
        return {"image_url": row["description"]}
    finally:
        cursor.close()
        conn.close()