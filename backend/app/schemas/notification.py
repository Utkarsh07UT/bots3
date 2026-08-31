from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


class NotificationPreferenceBase(BaseModel):
    email: str = Field(..., description="Recipient email address")
    name: Optional[str] = Field(None, max_length=128, description="Recipient friendly name")
    is_enabled: bool = Field(True, description="Master enable/disable switch")
    min_severity: str = Field("MEDIUM", description="Minimum severity to trigger alert (LOW, MEDIUM, HIGH, CRITICAL)")
    notify_critical: bool = Field(True, description="Send immediate email on CRITICAL alerts")
    notify_high: bool = Field(True, description="Send immediate email on HIGH alerts")
    notify_medium: bool = Field(True, description="Send email on MEDIUM alerts")
    notify_low: bool = Field(False, description="Send email on LOW alerts")
    quiet_hours_enabled: bool = Field(False, description="Enable quiet hours suppression")
    quiet_hours_start_utc: int = Field(22, ge=0, le=23, description="Quiet hours start hour (UTC 0-23)")
    quiet_hours_end_utc: int = Field(6, ge=0, le=23, description="Quiet hours end hour (UTC 0-23)")
    rate_limit_per_hour: int = Field(20, ge=1, le=1000, description="Max emails allowed per hour")


class NotificationPreferenceCreate(NotificationPreferenceBase):
    pass


class NotificationPreferenceUpdate(BaseModel):
    name: Optional[str] = None
    is_enabled: Optional[bool] = None
    min_severity: Optional[str] = None
    notify_critical: Optional[bool] = None
    notify_high: Optional[bool] = None
    notify_medium: Optional[bool] = None
    notify_low: Optional[bool] = None
    quiet_hours_enabled: Optional[bool] = None
    quiet_hours_start_utc: Optional[int] = Field(None, ge=0, le=23)
    quiet_hours_end_utc: Optional[int] = Field(None, ge=0, le=23)
    rate_limit_per_hour: Optional[int] = Field(None, ge=1, le=1000)


class NotificationPreferenceResponse(NotificationPreferenceBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class NotificationLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    alert_id: Optional[str] = None
    recipient: str
    channel: str
    provider: str
    status: str
    subject: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    sent_at: Optional[datetime] = None


class SendTestNotificationRequest(BaseModel):
    email: str = Field(..., description="Target email address to receive the test alert")
    provider: Optional[str] = Field(None, description="Optional override provider (console, smtp, resend, sendgrid)")
    severity: Optional[str] = Field("HIGH", description="Severity level for simulated test alert (CRITICAL, HIGH, MEDIUM, LOW)")


class SendTestNotificationResponse(BaseModel):
    success: bool
    provider: str
    recipient: str
    message: str
    details: Optional[dict] = None
