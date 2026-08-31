from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.db.models import ThreatAlert, NetworkFlow, BotMetric, BlockchainLog
from app.schemas.alert import ThreatAlertCreate, ThreatAlertUpdate
from typing import List, Optional

def get_alert(db: Session, alert_id: str) -> Optional[ThreatAlert]:
    return db.query(ThreatAlert).filter(ThreatAlert.alert_id == alert_id).first()

def get_alerts(db: Session, skip: int = 0, limit: int = 100) -> List[ThreatAlert]:
    return db.query(ThreatAlert).order_by(desc(ThreatAlert.created_at)).offset(skip).limit(limit).all()

def create_alert(db: Session, alert: ThreatAlertCreate) -> ThreatAlert:
    db_alert = ThreatAlert(**alert.model_dump())
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert

def update_alert_blockchain_status(
    db: Session, 
    alert_id: str, 
    tx_hash: str, 
    block_num: int
) -> Optional[ThreatAlert]:
    db_alert = get_alert(db, alert_id)
    if not db_alert:
        return None
    db_alert.blockchain_tx_hash = tx_hash
    db_alert.blockchain_verified = True
    db_alert.blockchain_block_num = block_num
    db.commit()
    db.refresh(db_alert)
    return db_alert

def create_blockchain_log(
    db: Session, 
    alert_id: str, 
    alert_hash: str, 
    tx_hash: str, 
    block_number: int, 
    contract_address: str, 
    sender_address: str
) -> BlockchainLog:
    db_log = BlockchainLog(
        alert_id=alert_id,
        alert_hash=alert_hash,
        tx_hash=tx_hash,
        block_number=block_number,
        contract_address=contract_address,
        sender_address=sender_address
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def get_bot_metrics(db: Session) -> List[BotMetric]:
    return db.query(BotMetric).all()

def get_recent_flows(db: Session, limit: int = 50) -> List[NetworkFlow]:
    return db.query(NetworkFlow).order_by(desc(NetworkFlow.timestamp)).limit(limit).all()
