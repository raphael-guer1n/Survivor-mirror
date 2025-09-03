from fastapi import FastAPI
from app.routers import users
from app.routers import auth
from app.routers import events
from app.routers import news
from app.routers import partners
from app.scheduler.sync_runner import register_scheduler
from app.services.sync import sync_all

app = FastAPI()

app.include_router(users.router, prefix="/api", tags=["users"])
app.include_router(auth.router)
app.include_router(events.router, prefix="/api", tags=["events"])
app.include_router(news.router, prefix="/api", tags=["news"])
app.include_router(partners.router, prefix="/api", tags=["news"])

@app.post("/admin/sync")
def admin_sync():
    return sync_all()

register_scheduler(app)

@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI middleware for JEB API"}