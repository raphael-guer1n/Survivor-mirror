from fastapi import APIRouter, HTTPException
from services.jeb_api import JEBAPIService

router = APIRouter()

@router.get("/users")
async def get_users():
    """
    Fetch all users from the JEB API and return the data to the frontend.
    """
    try:
        users = JEBAPIService.get_users()
        return users
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/users/{user_id}")
async def get_user(user_id: int):
    """
    Fetch a user by ID from the JEB API and return the data to the frontend.
    """
    try:
        user = JEBAPIService.get_user_by_id(user_id)
        return user
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/users/email/{email}")
async def get_user_by_email(email: str):
    """
    Fetch a user by email from the JEB API and return the data to the frontend.
    """
    try:
        user = JEBAPIService.get_user_by_email(email)
        return user
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/users/{user_id}/image")
async def get_user_image(user_id: int):
    """
    Fetch a user's image by ID from the JEB API and return the data to the frontend.
    """
    try:
        image_url = JEBAPIService.get_user_image(user_id)
        return {"image_url": image_url}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")