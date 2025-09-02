from fastapi import FastAPI
from app.routers import users
from app.routers import auth
from app.routers import events

app = FastAPI()

app.include_router(users.router, prefix="/api", tags=["Users"])
app.include_router(auth.router)
app.include_router(events.router, prefix="/api", tags=["Events"])

@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI middleware for JEB API"}