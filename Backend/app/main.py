from fastapi import FastAPI
from app.routers import auth

app = FastAPI(title="JEB Backend")

app.include_router(auth.router)

@app.get("/hello")
def hello():
    return {"message": "ok"}
