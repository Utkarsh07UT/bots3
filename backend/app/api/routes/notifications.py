import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.session import get_db
from app.db.models import NotificationPreference, NotificationLog
from app.schemas.notification import (
    NotificationPreferenceCreate,
    NotificationPreferenceUpdate,
    NotificationPreferenceResponse,
    NotificationLogResponse,
    SendTestNotificationRequest,
    SendTestNotificationResponse,
)
from app.notifications.service import notification_service

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/preferences", response_model=List[NotificationPreferenceResponse])
def list_preferences(db: Session = Depends(get_db)):
    """
    Retrieve all configured notification recipient preferences.
    """
    return db.query(NotificationPreference).order_by(desc(NotificationPreference.created_at)).all()


@router.post("/preferences", response_model=NotificationPreferenceResponse, status_code=status.HTTP_201_CREATED)
def create_or_update_preference(payload: NotificationPreferenceCreate, db: Session = Depends(get_db)):
    """
    Create a new notification recipient preference or update an existing one by email.
    """
    existing = db.query(NotificationPreference).filter(NotificationPreference.email == payload.email).first()
    if existing:
        for field, value in payload.model_dump().items():
            setattr(existing, field, value)
        db.commit()
        db.refresh(existing)
        return existing

    new_pref = NotificationPreference(
        id=str(uuid.uuid4()),
        **payload.model_dump()
    )
    db.add(new_pref)
    db.commit()
    db.refresh(new_pref)
    return new_pref


@router.put("/preferences/{preference_id}", response_model=NotificationPreferenceResponse)
def update_preference(preference_id: str, payload: NotificationPreferenceUpdate, db: Session = Depends(get_db)):
    """
    Update a notification preference by ID.
    """
    pref = db.query(NotificationPreference).filter(NotificationPreference.id == preference_id).first()
    if not pref:
        raise HTTPException(status_code=404, detail="Notification preference not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(pref, field, value)

    db.commit()
    db.refresh(pref)
    return pref


@router.delete("/preferences/{preference_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_preference(preference_id: str, db: Session = Depends(get_db)):
    """
    Delete a notification preference.
    """
    pref = db.query(NotificationPreference).filter(NotificationPreference.id == preference_id).first()
    if not pref:
        raise HTTPException(status_code=404, detail="Notification preference not found")

    db.delete(pref)
    db.commit()
    return None


@router.get("/logs", response_model=List[NotificationLogResponse])
def list_notification_logs(
    recipient: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """
    List historical notification delivery attempts and audit logs.
    """
    query = db.query(NotificationLog)
    if recipient:
        query = query.filter(NotificationLog.recipient == recipient)
    if status_filter:
        query = query.filter(NotificationLog.status == status_filter.upper())

    return query.order_by(desc(NotificationLog.sent_at)).limit(limit).all()


@router.post("/test", response_model=SendTestNotificationResponse)
async def send_test_notification(payload: SendTestNotificationRequest):
    """
    Dispatches an immediate simulated test notification to verify email provider connectivity.
    """
    result = await notification_service.send_test_notification(
        to_email=payload.email,
        provider_name=payload.provider,
        severity=payload.severity or "HIGH",
    )
    return SendTestNotificationResponse(**result)
