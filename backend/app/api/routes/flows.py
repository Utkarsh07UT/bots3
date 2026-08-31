# Cache bust: force Render to recompile this file
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.session import get_db
from app.db.models import NetworkFlow
from app.schemas.flow import NetworkFlowCreate, NetworkFlowResponse

router = APIRouter()


@router.get("/flows", response_model=list[NetworkFlowResponse])
def get_flows(limit: int = 50, db: Session = Depends(get_db)):
    flows = (
        db.query(NetworkFlow)
        .order_by(desc(NetworkFlow.timestamp))
        .limit(limit)
        .all()
    )
    return flows


@router.get("/flows/{flow_id}", response_model=NetworkFlowResponse)
def get_flow(flow_id: str, db: Session = Depends(get_db)):
    flow = db.query(NetworkFlow).filter(NetworkFlow.flow_id == flow_id).first()
    if not flow:
        raise HTTPException(status_code=404, detail="Flow not found")
    return flow


@router.post("/flows", response_model=NetworkFlowResponse)
def create_flow(flow: NetworkFlowCreate, db: Session = Depends(get_db)):
    db_flow = NetworkFlow(**flow.model_dump())
    db.add(db_flow)
    db.commit()
    db.refresh(db_flow)
    return db_flow