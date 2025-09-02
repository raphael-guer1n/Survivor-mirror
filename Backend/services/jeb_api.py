from app.core.config import JEB_API_KEY
import requests
from fastapi import HTTPException

class JEBAPIService:
    BASE_URL = "https://api.jeb-incubator.com"

    @staticmethod
    def get_users():
        url = f"{JEBAPIService.BASE_URL}/users"
        headers = {"X-Group-Authorization": JEB_API_KEY}
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Error fetching users: {response.text}"
            )

    @staticmethod
    def get_user_by_id(user_id: int):
        url = f"{JEBAPIService.BASE_URL}/users/{user_id}"
        headers = {"X-Group-Authorization": JEB_API_KEY}
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            raise HTTPException(status_code=404, detail="User not found")
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Error fetching user: {response.text}"
            )
