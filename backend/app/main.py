# Cache bust: force Render to recompile this file
import asyncio
import os

from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.alerts import router as alerts_router
from app.api.routes.bots import router as bots_router
from app.api.routes.flows import router as flows_router
from app.api.routes.blockchain import router as blockchain_router
from app.api.routes.mode import router as mode_router
from app.api.routes.notifications import router as notifications_router
from app.db.models import NetworkFlow
from app.db.session import SessionLocal, get_db


app = FastAPI(title="Cyber Threat Detection API")
app.include_router(alerts_router, prefix="/api")
app.include_router(bots_router, prefix="/api")
app.include_router(flows_router, prefix="/api")
app.include_router(blockchain_router, prefix="/api/blockchain")
app.include_router(mode_router, prefix="/api/mode")
app.include_router(notifications_router, prefix="/api")

default_origins = [
    "https://cyber-threat-detection.vercel.app",
    "https://cyber-threat-detection.onrender.com",
]
configured_origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "").split(",") if origin.strip()]
allowed_origins = list(set(default_origins + configured_origins))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://your-vercel-app.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}