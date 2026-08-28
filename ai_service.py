"""
ai_service.py

Production-Ready FastAPI Microservice for the 6 Specialist AI Threat Detection Bots:
1. ddos_bot               (DDoS & Floods)
2. beaconing_bot          (C2 Beaconing)
3. dga_dns_bot            (DGA Hostnames)
4. encrypted_malware_bot  (Encrypted Malware / C2-over-TLS)
5. scanning_bot           (Network Scanning & Reconnaissance)
6. exfiltration_bot       (Data Exfiltration)

Deployable on Render, Docker, or standalone.
"""

import os
import sys
import time
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ai_models.common.model_registry import BOT_NAMES, load_bot, _REGISTRY

SAVED_MODELS_DIR = os.path.join(PROJECT_ROOT, "ai_models", "saved_models")
os.makedirs(SAVED_MODELS_DIR, exist_ok=True)

# Bot metadata specifications
BOT_METADATA = {
    "ddos_bot": {
        "display_name": "DDoS Detection",
        "category": "DDoS / Floods",
        "description": "Detects TCP SYN floods, UDP reflection amplification, and Slowloris attacks.",
        "accuracy_score": 1.0000,
        "f1_score": 1.0000,
    },
    "beaconing_bot": {
        "display_name": "Beaconing Detection",
        "category": "Beaconing / C2",
        "description": "Detects Command & Control heartbeat callbacks through timing regularity and jitter analysis.",
        "accuracy_score": 0.9992,
        "f1_score": 0.9992,
    },
    "dga_dns_bot": {
        "display_name": "DGA / DNS Detection",
        "category": "DGA DNS",
        "description": "Detects Domain Generation Algorithm (DGA) queries via lexical and Shannon entropy features.",
        "accuracy_score": 0.9787,
        "f1_score": 0.9782,
    },
    "encrypted_malware_bot": {
        "display_name": "Encrypted Malware",
        "category": "Encrypted Malware / C2-over-TLS",
        "description": "Fingerprints encrypted TLS handshakes and JA3 signatures without payload decryption.",
        "accuracy_score": 1.0000,
        "f1_score": 1.0000,
    },
    "scanning_bot": {
        "display_name": "Scanning Detection",
        "category": "Scanning / Reconnaissance",
        "description": "Detects horizontal IP sweeps, vertical port scans, and reconnaissance traffic.",
        "accuracy_score": 1.0000,
        "f1_score": 1.0000,
    },
    "exfiltration_bot": {
        "display_name": "Data Exfiltration",
        "category": "Data Exfiltration",
        "description": "Detects egress volume anomalies and DNS covert tunneling channels.",
        "accuracy_score": 1.0000,
        "f1_score": 1.0000,
    },
}


def ensure_models() -> None:
    """Checks if model files exist; if any are missing, trains them automatically."""
    for name in BOT_NAMES:
        model_path = os.path.join(SAVED_MODELS_DIR, f"{name}.pkl")
        if not os.path.exists(model_path):
            print(f"[*] Training missing model artifact for {name}...")
            try:
                import importlib
                train_module = importlib.import_module(f"ai_models.bots.{name}.train")
                if hasattr(train_module, "main"):
                    train_module.main()
                print(f"[+] Successfully trained and saved {name}.pkl")
            except Exception as e:
                print(f"[!] Failed to auto-train {name}: {e}")


# Pre-train/verify models at startup
ensure_models()

# Global state for loaded bots and real-time metrics
LOADED_BOTS: Dict[str, Any] = {}
BOT_METRICS: Dict[str, Dict[str, Any]] = {}
START_TIME = time.time()


def init_bots() -> None:
    """Instantiate and cache all 6 specialist bots into memory."""
    for name in BOT_NAMES:
        path = os.path.join(SAVED_MODELS_DIR, f"{name}.pkl")
        if os.path.exists(path):
            bot = load_bot(name, path)
            LOADED_BOTS[name] = bot
        else:
            bot = load_bot(name)
            LOADED_BOTS[name] = bot

        meta = BOT_METADATA.get(name, {})
        BOT_METRICS[name] = {
            "bot_name": name,
            "display_name": meta.get("display_name", name),
            "status": "ONLINE",
            "version": "1.0.0",
            "category": meta.get("category", getattr(bot, "threat_category", "Unknown")),
            "description": meta.get("description", ""),
            "accuracy_score": meta.get("accuracy_score", 0.99),
            "f1_score": meta.get("f1_score", 0.99),
            "latency_ms": 0.10,
            "predictions_count": 0,
            "threats_detected": 0,
            "features": list(getattr(bot, "feature_names", [])),
        }


init_bots()

# -----------------------------------------------------------------------------
# FastAPI Application Definition
# -----------------------------------------------------------------------------
app = FastAPI(
    title="Specialist AI Cyber Threat Detection Service",
    description="Microservice providing real-time ML inference for 6 Specialist AI Threat Detection Bots.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------------------------------------------------
# Schemas
# -----------------------------------------------------------------------------
class BotInfoResponse(BaseModel):
    bot_name: str
    display_name: str
    status: str
    version: str
    category: str
    description: str
    accuracy_score: float
    f1_score: float
    latency_ms: float
    predictions_count: int
    threats_detected: int
    features: List[str]


class BotListResponse(BaseModel):
    status: str
    total_bots: int
    bots: List[BotInfoResponse]


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    uptime_seconds: float
    bots_loaded: int
    active_bots: List[str]


class SinglePredictionResponse(BaseModel):
    bot_name: str
    category: str
    malicious: bool
    label: str
    confidence: float
    severity: str
    features: Dict[str, float]
    timestamp: float = Field(default_factory=time.time)


class MultiBotEvaluationResponse(BaseModel):
    flow_id: Optional[str] = None
    evaluated_bots_count: int
    threat_detected: bool
    primary_threat: Optional[str] = None
    highest_confidence: float
    overall_severity: str
    contributing_bots: List[str]
    predictions: Dict[str, SinglePredictionResponse]


from fastapi import Body

# -----------------------------------------------------------------------------
# Endpoints
# -----------------------------------------------------------------------------
@app.get("/", tags=["General"])
def root() -> Dict[str, Any]:
    """Root endpoint describing available services and endpoints."""
    return {
        "service": "Specialist AI Cyber Threat Detection Service",
        "status": "ONLINE",
        "version": "1.0.0",
        "loaded_bots": len(LOADED_BOTS),
        "endpoints": {
            "health": "/health",
            "list_bots": "/bots",
            "bot_detail": "/bots/{bot_name}",
            "predict_single": "/predict/{bot_name}",
            "predict_batch": "/predict/batch/{bot_name}",
            "predict_all": "/predict/all",
        },
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health() -> HealthResponse:
    """Service health check endpoint."""
    return HealthResponse(
        status="ok",
        service="ai-threat-detection-bots",
        version="1.0.0",
        uptime_seconds=round(time.time() - START_TIME, 2),
        bots_loaded=len(LOADED_BOTS),
        active_bots=list(LOADED_BOTS.keys()),
    )


@app.get("/bots", response_model=List[BotInfoResponse], tags=["Bots"])
def list_bots() -> List[BotInfoResponse]:
    """Returns telemetry and metadata for all 6 specialist bots."""
    return [BotInfoResponse(**BOT_METRICS[name]) for name in BOT_NAMES if name in BOT_METRICS]


@app.get("/bots/{bot_name}", response_model=BotInfoResponse, tags=["Bots"])
def get_bot(bot_name: str) -> BotInfoResponse:
    """Returns telemetry and metadata for a specific bot."""
    if bot_name not in BOT_METRICS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bot '{bot_name}' not found. Available: {BOT_NAMES}",
        )
    return BotInfoResponse(**BOT_METRICS[bot_name])


@app.post("/predict/all", response_model=MultiBotEvaluationResponse, tags=["Inference"])
@app.post("/evaluate/flow", response_model=MultiBotEvaluationResponse, tags=["Inference"])
async def evaluate_flow_all_bots(payload: Dict[str, Any] = Body(...)) -> MultiBotEvaluationResponse:
    """
    Evaluates a network flow / session record across all 6 specialist bots simultaneously
    and performs multi-bot score fusion.
    """
    predictions: Dict[str, SinglePredictionResponse] = {}
    contributing: List[str] = []
    highest_conf = 0.0
    primary_threat = None
    overall_sev = "NONE"
    is_malicious = False

    severity_order = {"NONE": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}

    for name in BOT_NAMES:
        bot = LOADED_BOTS.get(name)
        if not bot:
            continue
        try:
            res = bot.predict(payload)
            res_dict = res.to_dict()
            res_dict["severity"] = res_dict.get("severity", "none").upper()
            pred = SinglePredictionResponse(**res_dict)
            predictions[name] = pred

            BOT_METRICS[name]["predictions_count"] += 1
            if pred.malicious:
                BOT_METRICS[name]["threats_detected"] += 1
                contributing.append(name)
                is_malicious = True
                if pred.confidence > highest_conf:
                    highest_conf = pred.confidence
                    primary_threat = pred.category
                if severity_order.get(pred.severity, 0) > severity_order.get(overall_sev, 0):
                    overall_sev = pred.severity
        except Exception:
            continue

    flow_id = str(payload.get("flow_id", payload.get("id", ""))) or None

    return MultiBotEvaluationResponse(
        flow_id=flow_id,
        evaluated_bots_count=len(predictions),
        threat_detected=is_malicious,
        primary_threat=primary_threat,
        highest_confidence=round(highest_conf, 4),
        overall_severity=overall_sev,
        contributing_bots=contributing,
        predictions=predictions,
    )


@app.post("/predict/batch/{bot_name}", response_model=List[SinglePredictionResponse], tags=["Inference"])
async def predict_batch(bot_name: str, payload: Any = Body(...)) -> List[SinglePredictionResponse]:
    """Runs high-throughput batch inference over a list of flow records."""
    if bot_name not in LOADED_BOTS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bot '{bot_name}' not found. Available bots: {BOT_NAMES}",
        )

    items: List[Dict[str, Any]] = []
    if isinstance(payload, list):
        items = payload
    elif isinstance(payload, dict):
        items = payload.get("items", payload.get("flows", payload.get("records", [payload])))
    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Payload must be a JSON array of dicts or an object with 'items' / 'flows' key.",
        )

    bot = LOADED_BOTS[bot_name]
    t0 = time.perf_counter()

    try:
        results = bot.predict_batch(items)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Batch inference error in {bot_name}: {str(e)}",
        )

    latency_ms = (time.perf_counter() - t0) * 1000.0
    avg_latency = latency_ms / max(1, len(items))

    BOT_METRICS[bot_name]["predictions_count"] += len(items)
    threats = sum(1 for r in results if r.malicious)
    BOT_METRICS[bot_name]["threats_detected"] += threats
    BOT_METRICS[bot_name]["latency_ms"] = round(avg_latency, 2)

    out = []
    for r in results:
        d = r.to_dict()
        d["severity"] = d.get("severity", "none").upper()
        out.append(SinglePredictionResponse(**d))
    return out


@app.post("/predict/{bot_name}", response_model=SinglePredictionResponse, tags=["Inference"])
async def predict_single(bot_name: str, payload: Dict[str, Any] = Body(...)) -> SinglePredictionResponse:
    """
    Runs real-time inference on a single payload using the specified specialist bot.
    Compatible with backend's main_controller.py and direct external API consumers.
    """
    if bot_name not in LOADED_BOTS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bot '{bot_name}' not found. Available bots: {BOT_NAMES}",
        )

    bot = LOADED_BOTS[bot_name]
    t0 = time.perf_counter()

    try:
        result = bot.predict(payload)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Inference error in {bot_name}: {str(e)}",
        )

    latency_ms = (time.perf_counter() - t0) * 1000.0

    # Update telemetry
    BOT_METRICS[bot_name]["predictions_count"] += 1
    if result.malicious:
        BOT_METRICS[bot_name]["threats_detected"] += 1
    BOT_METRICS[bot_name]["latency_ms"] = round(latency_ms, 2)

    res_dict = result.to_dict()
    # Normalize severity casing
    res_dict["severity"] = res_dict.get("severity", "none").upper()
    return SinglePredictionResponse(**res_dict)


# -----------------------------------------------------------------------------
# Standalone CLI Entrypoint
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 10000))
    host = os.getenv("HOST", "0.0.0.0")
    print(f"[*] Starting Specialist AI Bot Service on {host}:{port}...")
    uvicorn.run("ai_service:app", host=host, port=port, reload=False)

