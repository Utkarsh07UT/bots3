from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.crud import get_alert, update_alert_blockchain_status, create_blockchain_log
from app.blockchain.hasher import hash_alert
from app.blockchain.web3_client import blockchain_client

router = APIRouter()

@router.post("/log/{alert_id}")
def log_alert_to_blockchain(alert_id: str, db: Session = Depends(get_db)):
    """
    Computes hash of the alert and attempts to log it to the blockchain via the smart contract.
    Updates the database with the resulting transaction hash.
    """
    alert = get_alert(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    if alert.blockchain_verified:
        return {"status": "already_logged", "tx_hash": alert.blockchain_tx_hash}

    # Extract dict representation of the SQLAlchemy model for hashing
    alert_dict = {
        "alert_id": alert.alert_id,
        "title": alert.title,
        "severity": alert.severity,
        "attack_type": alert.attack_type,
        "source_ip": alert.source_ip,
        "target_ip": alert.target_ip,
        "confidence_score": alert.confidence_score
    }
    
    alert_hash = hash_alert(alert_dict)
    
    result = blockchain_client.log_alert_on_chain(alert_hash)
    
    if result.get("status") == "success":
        # Update alert and create log record
        update_alert_blockchain_status(
            db=db, 
            alert_id=alert_id, 
            tx_hash=result["tx_hash"], 
            block_num=result["block_number"]
        )
        
        create_blockchain_log(
            db=db,
            alert_id=alert_id,
            alert_hash=alert_hash,
            tx_hash=result["tx_hash"],
            block_number=result["block_number"],
            contract_address=result["contract"],
            sender_address=result["sender"]
        )
        
        return {"status": "success", "tx_hash": result["tx_hash"], "alert_hash": alert_hash}
    else:
        raise HTTPException(status_code=500, detail=result.get("error", "Failed to log on blockchain"))


@router.get("/verify/{alert_id}")
def verify_alert_on_blockchain(alert_id: str, db: Session = Depends(get_db)):
    """
    Computes the hash of the alert from the DB and queries the smart contract
    to verify if it was logged correctly.
    """
    alert = get_alert(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    alert_dict = {
        "alert_id": alert.alert_id,
        "title": alert.title,
        "severity": alert.severity,
        "attack_type": alert.attack_type,
        "source_ip": alert.source_ip,
        "target_ip": alert.target_ip,
        "confidence_score": alert.confidence_score
    }
    
    alert_hash = hash_alert(alert_dict)
    
    result = blockchain_client.verify_alert_on_chain(alert_hash)
    
    if result.get("status") == "success":
        return {
            "alert_id": alert_id,
            "alert_hash": alert_hash,
            "on_chain_verified": result["verified"],
            "timestamp": result.get("timestamp"),
            "sender": result.get("sender")
        }
    else:
        raise HTTPException(status_code=500, detail=result.get("error", "Failed to verify on blockchain"))
