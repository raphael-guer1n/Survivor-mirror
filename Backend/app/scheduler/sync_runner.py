from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from fastapi import FastAPI
from app.core.config import SYNC_INTERVAL_SECONDS
from app.services.sync import sync_all

def register_scheduler(app: FastAPI):
    scheduler = BackgroundScheduler(timezone="UTC")

    scheduler.add_job(
        func=sync_all,
        trigger=IntervalTrigger(seconds=SYNC_INTERVAL_SECONDS),
        id="sync_all_job",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )

    @app.on_event("startup")
    def _start():
        try:
            sync_all()
        except Exception:
            pass
        scheduler.start()

    @app.on_event("shutdown")
    def _stop():
        scheduler.shutdown(wait=False)
