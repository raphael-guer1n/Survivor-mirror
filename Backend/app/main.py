from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import users
from app.routers import auth
from app.routers import events
from app.scheduler.sync_runner import register_scheduler
from app.services.sync import sync_all

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/api", tags=["Users"])
app.include_router(auth.router)
app.include_router(events.router, prefix="/api", tags=["Events"])

@app.post("/admin/sync")
def admin_sync():
    return sync_all()

register_scheduler(app)

@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI middleware for JEB API"}