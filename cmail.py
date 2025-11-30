# cmail.py  — send emails using Brevo HTTP API (works on Render)
import os
import requests

BREVO_API_KEY = os.environ.get("BREVO_API_KEY")

def send_email(to: str, subject: str, body: str) -> bool:
    """Send a plain-text email via Brevo.
    Returns True on success, False on failure.
    """
    if not BREVO_API_KEY:
        print("BREVO_API_KEY is not set in environment")
        return False

    # use an email address you own (and ideally have verified in Brevo)
    sender_email = "kavuluriyogendra@gmail.com"
    sender_name = "Chat Application"

    payload = {
        "sender": {
            "name": sender_name,
            "email": sender_email,
        },
        "to": [
            {"email": to}
        ],
        "subject": subject,
        "textContent": body,
    }

    try:
        resp = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            headers={
                "api-key": BREVO_API_KEY,
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=10,
        )
    except Exception as e:
        print("Brevo request failed:", e)
        return False

    if resp.status_code == 201:
        print(f"Email sent successfully to {to}")
        return True
    else:
        print("Brevo email error:", resp.status_code, resp.text)
        return False

