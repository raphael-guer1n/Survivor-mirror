from fastapi import FastAPI
from app.routers import users
from app.routers import auth

app = FastAPI()

app.include_router(users.router, prefix="/api", tags=["Users"])
app.include_router(auth.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI middleware for JEB API"}