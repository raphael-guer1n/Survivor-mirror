from fastapi import APIRouter, HTTPException, Query, Depends
from app.db.connection import get_connection
from app.schemas.event import EventCreate, EventUpdate, EventOut, EventImage
from typing import List
from app.routers.auth import require_admin

router = APIRouter(prefix="/events", tags=["events"])


@router.get("/", response_model=List[EventOut])
def get_events(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id, name, dates, location, description, event_type, target_audience
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


@router.get("/{event_id}", response_model=EventOut)
def get_event(event_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id, name, dates, location, description, event_type, target_audience
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
            SELECT id, name, dates, location, description, event_type, target_audience
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
            SELECT id, name, dates, location, description, event_type, target_audience
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


@router.get("/{event_id}/image", response_model=EventImage)
def get_event_image(event_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT description FROM events WHERE id = %s", (event_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Event not found")
        return {"image_url": row["description"]}
    finally:
        cursor.close()
        conn.close()
