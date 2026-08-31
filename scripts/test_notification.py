import os
import sys
import asyncio
import argparse
from pathlib import Path

# Add backend directory to sys.path
backend_path = Path(__file__).resolve().parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from app.notifications.service import notification_service


def main():
    parser = argparse.ArgumentParser(description="Dispatch a simulated threat alert test notification.")
    parser.add_argument("--email", type=str, default="analyst@thethirdeye.sec", help="Recipient email address")
    parser.add_argument("--provider", type=str, default="console", choices=["console", "smtp", "resend", "sendgrid"], help="Notification provider")
    parser.add_argument("--severity", type=str, default="CRITICAL", choices=["CRITICAL", "HIGH", "MEDIUM", "LOW"], help="Alert severity")

    args = parser.parse_args()

    print(f"\n[*] Sending simulated {args.severity} alert to {args.email} via '{args.provider}' provider...")
    res = asyncio.run(
        notification_service.send_test_notification(
            to_email=args.email,
            provider_name=args.provider,
            severity=args.severity,
        )
    )

    if res.get("success"):
        print(f"[+] Success: {res.get('message')}")
    else:
        print(f"[-] Failed: {res.get('message')}")


if __name__ == "__main__":
    main()
