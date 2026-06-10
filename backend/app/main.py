from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import images, reports
import os

app = FastAPI(title="PDI Arteterapia API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(images.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")

@app.get("/health")
def health():
    return {"status": "ok"}