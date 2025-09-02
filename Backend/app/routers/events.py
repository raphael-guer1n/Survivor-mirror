from fastapi import APIRouter, HTTPException, Query
from services.jeb_api import JEBAPIService
from app.schemas.event import Event, EventImage

router = APIRouter()

@router.get("/events", response_model=list[Event])
async def get_events(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1)):
    """
    Fetch a list of events from the JEB API.
    """
    try:
        events = JEBAPIService.get_events(skip=skip, limit=limit)
        return events
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/events/{event_id}", response_model=Event)
async def get_event(event_id: int):
    """
    Fetch a specific event by ID from the JEB API.
    """
    try:
        event = JEBAPIService.get_event_by_id(event_id)
        return event
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/events/{event_id}/image", response_model=EventImage)
async def get_event_image(event_id: int):
    """
    Fetch the image URL for a specific event by ID from the JEB API.
    """
    try:
        image_url = JEBAPIService.get_event_image(event_id)
        return {"image_url": image_url}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")