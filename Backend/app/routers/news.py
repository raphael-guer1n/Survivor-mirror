from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Depends
from typing import List
from app.db.connection import get_connection
from app.schemas.news import NewsCreate, NewsUpdate, NewsOut
from app.routers.auth import require_founder, check_founder_of_startup
from app.utils.s3 import upload_file_to_s3, generate_presigned_url
from app.schemas.event import EventImage

router = APIRouter(prefix="/news", tags=["news"])

@router.get("/", response_model=List[NewsOut])
def get_news(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id, title, news_date, location, category, startup_id, description, image_s3_key
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

@router.get("/most-viewed", response_model=list[NewsOut])
def get_most_viewed_news(limit: int = Query(10, ge=1, le=100)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id, title, news_date, location, category, startup_id, description, image_s3_key,
                   view_count
            FROM news
            ORDER BY view_count DESC
            LIMIT %s
            """,
            (limit,),
        )
        news = cursor.fetchall()
        if not news:
            raise HTTPException(status_code=404, detail="No news found")
        return news
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
            SELECT id, title, news_date, location, category, startup_id, description, image_s3_key
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
def create_news(news: NewsCreate, user=Depends(require_founder)):
    check_founder_of_startup(user, news.startup_id)
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
            """
            SELECT id, title, news_date, location, category, startup_id, description, image_s3_key
            FROM news WHERE id = %s
            """,
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
def update_news(news_id: int, news: NewsUpdate, user=Depends(require_founder)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, startup_id FROM news WHERE id = %s", (news_id,))
        news_row = cursor.fetchone()
        if not news_row:
            raise HTTPException(status_code=404, detail="News item not found")
        startup_id = news_row["startup_id"]
        check_founder_of_startup(user, startup_id)
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
            """
            SELECT id, title, news_date, location, category, startup_id, description, image_s3_key
            FROM news WHERE id = %s
            """,
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
def delete_news(news_id: int, user=Depends(require_founder)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, startup_id FROM news WHERE id = %s", (news_id,))
        news_row = cursor.fetchone()
        if not news_row:
            raise HTTPException(status_code=404, detail="News item not found")
        startup_id = news_row["startup_id"]
        check_founder_of_startup(user, startup_id)

        cursor.execute("DELETE FROM news WHERE id = %s", (news_id,))
        conn.commit()
        return {"message": f"News item {news_id} deleted successfully"}
    finally:
        cursor.close()
        conn.close()

async def upload_news_image(news_id: int, file: UploadFile = File(...)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id FROM news WHERE id = %s", (news_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="News item not found")
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Invalid file type")
        key = f"news/{news_id}/{file.filename}"
        url = upload_file_to_s3(file.file, key, file.content_type)
        cursor.execute("UPDATE news SET image_s3_key=%s WHERE id=%s", (key, news_id))
        conn.commit()
        return {"image_url": url}
    finally:
        cursor.close()
        conn.close()

@router.get("/{news_id}/image", response_model=EventImage)
def get_news_image(news_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT image_s3_key FROM news WHERE id = %s", (news_id,))
        row = cursor.fetchone()
        if not row or not row["image_s3_key"]:
            raise HTTPException(status_code=404, detail="Image not found")
        url = generate_presigned_url(row["image_s3_key"])
        return {"image_url": url}
    finally:
        cursor.close()
        conn.close()

@router.put("/{news_id}/image", response_model=EventImage)
async def update_news_image(news_id: int, file: UploadFile = File(...)):
    return await upload_news_image(news_id, file)

@router.delete("/{news_id}/image")
def delete_news_image(news_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT image_s3_key FROM news WHERE id = %s", (news_id,))
        row = cursor.fetchone()
        if not row or not row[0]:
            raise HTTPException(status_code=404, detail="Image not found")
        key = row[0]
        cursor.execute("UPDATE news SET image_s3_key=NULL WHERE id=%s", (news_id,))
        conn.commit()
        return {"message": f"Image for news {news_id} deleted successfully"}
    finally:
        cursor.close()
        conn.close()

@router.post("/{news_id}/view")
def increment_news_view(news_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, view_count FROM news WHERE id = %s", (news_id,))
        news = cursor.fetchone()
        if not news:
            raise HTTPException(status_code=404, detail="News not found")
        cursor.execute(
            "UPDATE news SET view_count = view_count + 1 WHERE id = %s", (news_id,)
        )
        conn.commit()
        return {"news_id": news_id, "new_view_count": news["view_count"] + 1}
    finally:
        cursor.close()
        conn.close()

@router.get("/{news_id}/view")
def get_news_view_count(news_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, view_count FROM news WHERE id = %s", (news_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="News not found")
        return {"news_id": row["id"], "view_count": row["view_count"]}
    finally:
        cursor.close()
        conn.close()

@router.get("/views/total")
def get_total_news_views():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT SUM(view_count) FROM news")
        total = cursor.fetchone()[0] or 0
        return {"total_views": total}
    finally:
        cursor.close()
        conn.close()
