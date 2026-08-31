from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.config import settings

router = APIRouter()

class ModeSwitchRequest(BaseModel):
    mode: str  # "live" or "replay"

@router.get("/")
def get_mode():
    return {"current_mode": settings.APP_MODE}

@router.post("/switch")
def switch_mode(request: ModeSwitchRequest):
    if request.mode not in ("live", "replay"):
        raise HTTPException(status_code=400, detail="Invalid mode. Must be 'live' or 'replay'.")
    
    # In a real app, this would dynamically stop the ReplayEngine/LiveCapture and start the other.
    # For now, we just update the settings object.
    settings.APP_MODE = request.mode
    
    return {"status": "success", "new_mode": settings.APP_MODE}
