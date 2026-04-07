from fastapi import FastAPI
from api.v1.api_router import v1_router

app = FastAPI(title="Mi API con Arch Linux Vibes")

app.include_router(v1_router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {"status": "running"}
