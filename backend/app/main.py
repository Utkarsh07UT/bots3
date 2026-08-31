# Cache bust: force Render to recompile this file
import asyncio
import os

from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.api.routes.alerts import router as alerts_router
from app.api.routes.bots import router as bots_router
from app.api.routes.flows import router as flows_router
from app.api.routes.blockchain import router as blockchain_router
from app.api.routes.mode import router as mode_router
from app.api.routes.notifications import router as notifications_router
from app.db.models import NetworkFlow
from app.db.session import SessionLocal, get_db
from app.services.bot_health import refresh_bot_metrics
from app.services.chat import build_response

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
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\.vercel\.app|https://.*\.onrender\.com",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


@app.post("/api/chat")
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    return {"response": build_response(request.message, db)}


@app.websocket("/ws/flows")
async def flow_stream(websocket: WebSocket):
    """Push new flow records by polling the database; suitable for a simple deployment."""
    await websocket.accept()
    seen_ids: set[str] = set()
    try:
        while True:
            db = SessionLocal()
            try:
                flows = db.query(NetworkFlow).order_by(desc(NetworkFlow.timestamp)).limit(50).all()
                initial_snapshot = not seen_ids
                for flow in reversed(flows):
                    if flow.id in seen_ids or initial_snapshot:
                        continue
                    await websocket.send_json({
                        "id": flow.id, "flow_id": flow.flow_id, "src_ip": flow.src_ip,
                        "dst_ip": flow.dst_ip, "src_port": flow.src_port, "dst_port": flow.dst_port,
                        "protocol": flow.protocol, "duration": float(flow.duration or 0),
                        "bytes_in": flow.bytes_in, "bytes_out": flow.bytes_out, "pkts_in": flow.pkts_in,
                        "pkts_out": flow.pkts_out, "tcp_flags": flow.tcp_flags, "is_attack": flow.is_attack,
                        "attack_type": flow.attack_type, "timestamp": flow.timestamp.isoformat(),
                    })
                seen_ids.update(flow.id for flow in flows)
                if len(seen_ids) > 200:
                    seen_ids = {flow.id for flow in flows}
            finally:
                db.close()
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        return


from app.db.session import SessionLocal, get_db, Base, engine
from app.services.pipeline import process_flows_pipeline


@app.on_event("startup")
async def start_background_tasks() -> None:
    # Ensure database schema exists (useful for SQLite local dev or new DBs)
    try:
        Base.metadata.create_all(bind=engine)
    except Exception:
        pass

    async def monitor() -> None:
        while True:
            try:
                await asyncio.to_thread(refresh_bot_metrics)
            except Exception:
                pass
            await asyncio.sleep(30)

    asyncio.create_task(monitor())
    asyncio.create_task(process_flows_pipeline())
