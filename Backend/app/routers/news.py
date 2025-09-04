from fastapi import APIRouter, HTTPException, Query
from app.db.connection import get_connection
from app.schemas.news import NewsCreate, NewsUpdate, NewsOut

router = APIRouter(prefix="/news", tags=["news"])

@router.get("/", response_model=list[NewsOut])
def get_news(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id, title, news_date, location, category, startup_id, description
            FROM news
            ORDER BY news_date DESC
            LIMIT %s OFFSET %s
            """,
            (limit, skip),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

@router.get("/{news_id}", response_model=NewsOut)
def get_news_item(news_id: int):
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
        news = cursor.fetchone()
        if not news:
            raise HTTPException(status_code=404, detail="News item not found")
        return news
    finally:
        cursor.close()
        conn.close()

@router.post("/", response_model=NewsOut)
def create_news(news: NewsCreate):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            INSERT INTO news (title, news_date, location, category, startup_id, description)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                news.title,
                news.news_date,
                news.location,
                news.category,
                news.startup_id if news.startup_id else None,
                news.description,
            ),
        )
        conn.commit()
        new_id = cursor.lastrowid
        cursor.execute(
            "SELECT id, title, news_date, location, category, startup_id, description FROM news WHERE id = %s",
            (new_id,),
        )
        return cursor.fetchone()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"DB error: {e}")
    finally:
        cursor.close()
        conn.close()

@router.put("/{news_id}", response_model=NewsOut)
def update_news(news_id: int, news: NewsUpdate):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id FROM news WHERE id = %s", (news_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="News item not found")

        fields = []
        values = []
        for field, value in news.dict(exclude_unset=True).items():
            if field == "startup_id" and value == 0:
                value = None
            fields.append(f"{field}=%s")
            values.append(value)

        if not fields:
            raise HTTPException(status_code=400, detail="No fields to update")

        values.append(news_id)
        sql = f"UPDATE news SET {', '.join(fields)} WHERE id = %s"
        cursor.execute(sql, tuple(values))
        conn.commit()

        cursor.execute(
            "SELECT id, title, news_date, location, category, startup_id, description FROM news WHERE id = %s",
            (news_id,),
        )
        return cursor.fetchone()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"DB error: {e}")
    finally:
        cursor.close()
        conn.close()

@router.delete("/{news_id}")
def delete_news(news_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM news WHERE id = %s", (news_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="News item not found")

        cursor.execute("DELETE FROM news WHERE id = %s", (news_id,))
        conn.commit()
        return {"message": f"News item {news_id} deleted successfully"}
    finally:
        cursor.close()
        conn.close()
