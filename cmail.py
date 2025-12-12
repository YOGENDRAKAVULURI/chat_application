# cmail.py — Resend Email Sender (HTTPS API, no SMTP)
import os
import requests

RESEND_API_KEY = os.environ.get("RESEND_API_KEY")

def send_email(to: str, subject: str, body: str) -> bool:
    """Send a plain-text email using Resend HTTP API."""

    if not RESEND_API_KEY:
        print("ERROR: RESEND_API_KEY not found in environment.")
        return False

    url = "https://api.resend.com/emails"

    payload = {
        "from": "Chat App <onboarding@resend.dev>",   # Default verified sender
        "to": [to],
        "subject": subject,
        "text": body
    }

    try:
        resp = requests.post(
            url,
            json=payload,
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json"
            },
            timeout=10
        )

        if resp.status_code in (200, 202):
            print(f"Email sent successfully to {to}")
            return True
        else:
            print("Resend email error:", resp.status_code, resp.text)
            return False

    except Exception as e:
        print("Resend request failed:", e)
        return False
