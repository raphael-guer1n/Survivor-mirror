from fastapi import APIRouter, HTTPException, Query
from app.db.connection import get_connection
from app.schemas.event import Event, EventImage

router = APIRouter(prefix="/events", tags=["events"])

@router.get("/", response_model=list[Event])
def get_events(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, name, dates, location, description, event_type, target_audience FROM events LIMIT %s OFFSET %s", (limit, skip))
        events = cursor.fetchall()
        return events
    finally:
        cursor.close()
        conn.close()


@router.get("/{event_id}", response_model=Event)
def get_event(event_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, name, dates, location, description, event_type, target_audience FROM events WHERE id = %s", (event_id,))
        event = cursor.fetchone()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        return event
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