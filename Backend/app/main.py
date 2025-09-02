from fastapi import FastAPI
from app.routers import auth
from app.scheduler.sync_runner import register_scheduler
from app.services.sync import sync_all

app = FastAPI(title="JEB Backend")

app.include_router(auth.router)

@app.post("/admin/sync")
def admin_sync():
    return sync_all()

register_scheduler(app)

@app.get("/hello")
def hello():
    return {"message": "ok"}
