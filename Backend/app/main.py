from fastapi import FastAPI
from app.routers import auth

app = FastAPI(title="JEB Backend")

# Regroupe toutes tes routes ici
app.include_router(auth.router)

# Petit endpoint de test
@app.get("/hello")
def hello():
    return {"message": "ok"}
