# 📧 Real-Time Alert Notification System

The **TheThirdEYE Cyber Threat Operations Center** includes an enterprise-grade, asynchronous email and alert notification engine. Whenever the **Main Controller (Score Fusion)** or specialist AI bots detect malicious network traffic, the notification engine automatically evaluates threat severity, checks recipient policies, renders responsive dark-mode cyber alerts, and dispatches them via the configured email provider.

---

## 🏗️ Architecture & Data Flow

```
[ Network Flow Ingestion ]
           │
           ▼
[ Specialist AI Bots Inference ] (DDoS, Beaconing, DGA, Malware, Scan, Exfiltration)
           │
           ▼
[ Main Controller (Score Fusion) ]
           │
           ▼ (ThreatAlert Created)
[ NotificationService.notify_alert_background() ]
           │
  ┌────────┴─────────────────────────────────┐
  ▼                                          ▼
[ Rule Evaluation ]                     [ Rate Limiter ]
  - Severity Filter (CRITICAL/HIGH)        - Max N emails/hour/recipient
  - User Preferences                       - Prevents alert storms
  - Quiet Hours (UTC) with Crit Override
           │
           ▼ (If Allowed)
[ Jinja2 Template Renderer ]
  - alert_email.html (Dark-mode responsive cyber email)
  - alert_email.txt (Plaintext fallback)
           │
           ▼
[ Multi-Provider Dispatcher (w/ Exponential Backoff) ]
  ├── Console Provider   (Local dev & terminal logs)
  ├── SMTP Provider      (Gmail, Amazon SES, Mailgun, TLS/SSL)
  ├── Resend Provider    (Modern HTTP API)
  └── SendGrid Provider  (SendGrid v3 REST API)
           │
           ▼
[ NotificationLog Audit Table ] (Success, Failure, Latency, Retries)
```

---

## ⚙️ Configuration Reference

Configure the following environment variables in `backend/.env` (or via your cloud provider dashboard):

| Variable | Type | Default | Description |
| :--- | :---: | :---: | :--- |
| `EMAIL_NOTIFICATIONS_ENABLED` | `bool` | `true` | Master switch for all notification dispatches |
| `EMAIL_PROVIDER` | `string` | `console` | Select provider: `console`, `smtp`, `resend`, `sendgrid` |
| `DEFAULT_ALERT_EMAILS` | `string` | `security-team@thethirdeye.sec` | Comma-separated fallback alert recipients |
| `FRONTEND_BASE_URL` | `string` | `https://cyber-threat-detection.vercel.app` | Base URL for dashboard deep links in emails |
| `NOTIFICATION_RATE_LIMIT_PER_HOUR` | `int` | `20` | Maximum notification emails per recipient per hour |
| `NOTIFICATION_RETRY_ATTEMPTS` | `int` | `3` | Number of retry attempts with exponential backoff on network failures |

### 1. Console Provider (`EMAIL_PROVIDER=console`)
No external credentials required. Prints beautifully formatted email payloads to terminal logs. Ideal for local development, unit testing, and isolated staging.

### 2. SMTP Provider (`EMAIL_PROVIDER=smtp`)
```ini
EMAIL_PROVIDER=smtp
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=alerts@your-domain.com
SMTP_PASSWORD=your-app-password
SMTP_USE_TLS=true
SMTP_FROM_EMAIL=alerts@thethirdeye.sec
SMTP_FROM_NAME=TheThirdEYE SOC Alerts
```

### 3. Resend API Provider (`EMAIL_PROVIDER=resend`)
```ini
EMAIL_PROVIDER=resend
RESEND_API_KEY=re_1234567890abcdef
SMTP_FROM_EMAIL=alerts@your-verified-domain.com
SMTP_FROM_NAME=TheThirdEYE SOC Alerts
```

### 4. SendGrid Provider (`EMAIL_PROVIDER=sendgrid`)
```ini
EMAIL_PROVIDER=sendgrid
SENDGRID_API_KEY=SG.1234567890abcdef
SMTP_FROM_EMAIL=alerts@your-verified-domain.com
SMTP_FROM_NAME=TheThirdEYE SOC Alerts
```

---

## 🛡️ Severity & Policy Rules

The notification rule engine (`app/notifications/rules.py`) enforces strict triage rules:

1. **`CRITICAL` Alerts:** Immediate dispatch. Overrides quiet hours to ensure emergency SOC awareness.
2. **`HIGH` Alerts:** Immediate dispatch during standard operating hours.
3. **`MEDIUM` Alerts:** Dispatched if the user preference has `notify_medium=True` (enabled by default).
4. **`LOW` / `BENIGN` Alerts:** Suppressed from direct real-time emails by default to prevent inbox fatigue.

### Quiet Hours
Recipients can define quiet hours in UTC (e.g., `quiet_hours_start_utc=22`, `quiet_hours_end_utc=6`). During quiet hours, `MEDIUM` and `HIGH` alerts are suppressed and logged as `QUIET_HOURS`. `CRITICAL` alerts bypass quiet hours automatically.

### Rate Limiting & Anti-Storm Protection
The rate limiter checks `notification_logs` within a rolling 60-minute sliding window. If a burst of alerts exceeds `rate_limit_per_hour` (default: 20/hr), excess alerts are flagged as `RATE_LIMITED` and recorded in the database without overwhelming the mail server.

---

## 📡 REST API Reference

All routes are mounted under `/api/notifications`:

### 1. Send Simulated Test Email
```http
POST /api/notifications/test
Content-Type: application/json

{
  "email": "analyst@thethirdeye.sec",
  "provider": "console",
  "severity": "HIGH"
}
```
**Response (200 OK):**
```json
{
  "success": true,
  "provider": "console",
  "recipient": "analyst@thethirdeye.sec",
  "message": "Test email sent successfully",
  "details": {
    "success": true,
    "provider": "console",
    "message_id": "console-8f3a9e1d4b2c",
    "error": null
  }
}
```

### 2. List & Update Notification Preferences
* **`GET /api/notifications/preferences`**: List all recipient settings.
* **`POST /api/notifications/preferences`**: Add or update user preferences.
```json
{
  "email": "lead-analyst@thethirdeye.sec",
  "name": "SOC Incident Lead",
  "is_enabled": true,
  "min_severity": "HIGH",
  "notify_critical": true,
  "notify_high": true,
  "notify_medium": false,
  "notify_low": false,
  "quiet_hours_enabled": true,
  "quiet_hours_start_utc": 23,
  "quiet_hours_end_utc": 7,
  "rate_limit_per_hour": 15
}
```

### 3. View Delivery & Audit Logs
* **`GET /api/notifications/logs?status=SUCCESS&limit=50`**: View delivery audit logs with timestamp, provider, subject, retry count, and errors.

---

## 🧪 Testing Locally

Run the notification test suite:
```bash
pytest backend/tests/test_notifications.py -v
```
To trigger a live test email via CLI:
```bash
python -c "
import asyncio
from app.notifications.service import notification_service
res = asyncio.run(notification_service.send_test_notification('analyst@thethirdeye.sec', 'console', 'CRITICAL'))
print(res)
"
```
