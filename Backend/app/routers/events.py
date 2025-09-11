from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Depends
from app.db.connection import get_connection
from app.schemas.event import EventCreate, EventUpdate, EventOut, EventImage
from typing import List
from app.utils.s3 import upload_file_to_s3, generate_presigned_url
from app.routers.auth import require_admin

router = APIRouter(prefix="/events", tags=["events"])

@router.get("/", response_model=List[EventOut])
def get_events(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id, name, dates, location, description, event_type, target_audience, image_s3_key
            FROM events
            ORDER BY id DESC
            LIMIT %s OFFSET %s
            """,
            (limit, skip),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

@router.get("/most-viewed", response_model=list[EventOut])
def get_most_viewed_event(limit: int = Query(10, ge=1, le=100)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id, name, dates, location, description, event_type, target_audience, image_s3_key,
                   view_count
            FROM events
            ORDER BY view_count DESC
            LIMIT %s
            """,
            (limit,),
        )
        event = cursor.fetchall()
        if not event:
            raise HTTPException(status_code=404, detail="No event found")
        return event
    finally:
        cursor.close()
        conn.close()

@router.get("/{event_id}", response_model=EventOut)
def get_event(event_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id, name, dates, location, description, event_type, target_audience, image_s3_key
            FROM events
            WHERE id = %s
            """,
            (event_id,),
        )
        event = cursor.fetchone()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        return event
    finally:
        cursor.close()
        conn.close()

@router.post("/", response_model=EventOut)
def create_event(event: EventCreate, admin=Depends(require_admin)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            INSERT INTO events (name, dates, location, description, event_type, target_audience)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                event.name,
                event.dates,
                event.location,
                event.description,
                event.event_type,
                event.target_audience,
            ),
        )
        conn.commit()
        new_id = cursor.lastrowid
        cursor.execute(
            """
            SELECT id, name, dates, location, description, event_type, target_audience, image_s3_key
            FROM events WHERE id = %s
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

@router.put("/{event_id}", response_model=EventOut)
def update_event(event_id: int, event: EventUpdate, admin=Depends(require_admin)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id FROM events WHERE id = %s", (event_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Event not found")
        fields = []
        values = []
        for field, value in event.dict(exclude_unset=True).items():
            fields.append(f"{field}=%s")
            values.append(value)
        if not fields:
            raise HTTPException(status_code=400, detail="No fields to update")
        values.append(event_id)
        sql = f"UPDATE events SET {', '.join(fields)} WHERE id = %s"
        cursor.execute(sql, tuple(values))
        conn.commit()
        cursor.execute(
            """
            SELECT id, name, dates, location, description, event_type, target_audience, image_s3_key
            FROM events WHERE id = %s
            """,
            (event_id,),
        )
        return cursor.fetchone()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"DB error: {e}")
    finally:
        cursor.close()
        conn.close()

@router.delete("/{event_id}")
def delete_event(event_id: int, admin=Depends(require_admin)):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM events WHERE id = %s", (event_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Event not found")
        cursor.execute("DELETE FROM events WHERE id = %s", (event_id,))
        conn.commit()
        return {"message": f"Event {event_id} deleted successfully"}
    finally:
        cursor.close()
        conn.close()

@router.post("/{event_id}/image", response_model=EventImage)
async def upload_event_image(event_id: int, file: UploadFile = File(...)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id FROM events WHERE id = %s", (event_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Event not found")
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Invalid file type")
        key = f"events/{event_id}/{file.filename}"
        url = upload_file_to_s3(file.file, key, file.content_type)
        cursor.execute("UPDATE events SET image_s3_key=%s WHERE id=%s", (key, event_id))
        conn.commit()
        return {"image_url": url}
    finally:
        cursor.close()
        conn.close()

@router.get("/{event_id}/image", response_model=EventImage)
def get_event_image(event_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT image_s3_key FROM events WHERE id = %s", (event_id,))
        row = cursor.fetchone()
        if not row or not row["image_s3_key"]:
            raise HTTPException(status_code=404, detail="Image not found")
        url = generate_presigned_url(row["image_s3_key"])
        return {"image_url": url}
    finally:
        cursor.close()
        conn.close()

@router.put("/{event_id}/image", response_model=EventImage)
async def update_event_image(event_id: int, file: UploadFile = File(...)):
    return await upload_event_image(event_id, file)

@router.delete("/{event_id}/image")
def delete_event_image(event_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT image_s3_key FROM events WHERE id = %s", (event_id,))
        row = cursor.fetchone()
        if not row or not row[0]:
            raise HTTPException(status_code=404, detail="Image not found")
        key = row[0]
        cursor.execute("UPDATE events SET image_s3_key=NULL WHERE id=%s", (event_id,))
        conn.commit()

        return {"message": f"Image for event {event_id} deleted successfully"}
    finally:
        cursor.close()
        conn.close()

@router.post("/{event_id}/view")
def increment_event_view(event_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, view_count FROM events WHERE id = %s", (event_id,))
        event = cursor.fetchone()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        cursor.execute(
            "UPDATE events SET view_count = view_count + 1 WHERE id = %s", (event_id,)
        )
        conn.commit()
        return {"event_id": event_id, "new_view_count": event["view_count"] + 1}
    finally:
        cursor.close()
        conn.close()

@router.get("/{event_id}/view")
def get_event_view_count(event_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, view_count FROM events WHERE id = %s", (event_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Event not found")
        return {"event_id": row["id"], "view_count": row["view_count"]}
    finally:
        cursor.close()
        conn.close()

@router.get("/views/total")
def get_total_event_views():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT SUM(view_count) FROM events")
        total = cursor.fetchone()[0] or 0
        return {"total_views": total}
    finally:
        cursor.close()
        conn.close()
