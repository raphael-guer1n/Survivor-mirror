from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, users, events, news, partners, investors, startups
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

app.include_router(users.router, prefix="/api", tags=["users"])
app.include_router(auth.router)
app.include_router(events.router, prefix="/api", tags=["events"])
app.include_router(news.router, prefix="/api", tags=["news"])
app.include_router(partners.router, prefix="/api", tags=["partners"])
app.include_router(investors.router, prefix="/api", tags=["investors"])
app.include_router(startups.router, prefix="/api", tags=["startups"])

@app.post("/admin/sync")
def admin_sync():
    return sync_all()

register_scheduler(app)

@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI middleware for JEB API"}