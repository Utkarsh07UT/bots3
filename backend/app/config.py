import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # --- General & Runtime Mode ---
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    APP_MODE = os.getenv("APP_MODE", "replay")  # replay | live
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))

    # --- PostgreSQL Persistence ---
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test_threatlens.db")

    # --- Redis Streaming & Event Bus ---
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")

    # --- Web3 & Blockchain Audit Trail ---
    BLOCKCHAIN_ENABLED = os.getenv("BLOCKCHAIN_ENABLED", "false").lower() == "true"
    WEB3_RPC_URL = os.getenv("WEB3_RPC_URL", "")
    SMART_CONTRACT_ADDRESS = os.getenv("SMART_CONTRACT_ADDRESS", "")
    SIGNER_PRIVATE_KEY = os.getenv("SIGNER_PRIVATE_KEY", "")

    # --- AI Models & Detection Thresholds ---
    DDOS_PPS_THRESHOLD = int(os.getenv("DDOS_PPS_THRESHOLD", "10000"))
    BEACON_JITTER_TOLERANCE = float(os.getenv("BEACON_JITTER_TOLERANCE", "0.10"))
    DGA_ENTROPY_THRESHOLD = float(os.getenv("DGA_ENTROPY_THRESHOLD", "3.85"))
    EXFILTRATION_OUTBOUND_RATIO = float(os.getenv("EXFILTRATION_OUTBOUND_RATIO", "50.0"))

    # --- Ingestion Engine ---
    REPLAY_SPEED_MULTIPLIER = float(os.getenv("REPLAY_SPEED_MULTIPLIER", "1.0"))
    CAPTURE_INTERFACE = os.getenv("CAPTURE_INTERFACE", "eth0")

    # --- Email & Alert Notifications ---
    EMAIL_NOTIFICATIONS_ENABLED = os.getenv("EMAIL_NOTIFICATIONS_ENABLED", "true").lower() == "true"
    EMAIL_PROVIDER = os.getenv("EMAIL_PROVIDER", "console").lower()  # console | smtp | resend | sendgrid
    
    # SMTP Provider Settings
    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
    SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "alerts@thethirdeye.sec")
    SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "TheThirdEYE SOC Alerts")

    # Modern API Providers (Resend / SendGrid)
    RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")

    # Notification Defaults & Rate Limits
    DEFAULT_ALERT_EMAILS = [e.strip() for e in os.getenv("DEFAULT_ALERT_EMAILS", "security-team@thethirdeye.sec").split(",") if e.strip()]
    NOTIFICATION_RATE_LIMIT_PER_HOUR = int(os.getenv("NOTIFICATION_RATE_LIMIT_PER_HOUR", "20"))
    NOTIFICATION_RETRY_ATTEMPTS = int(os.getenv("NOTIFICATION_RETRY_ATTEMPTS", "3"))
    FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "https://cyber-threat-detection.vercel.app").rstrip("/")

settings = Settings()
