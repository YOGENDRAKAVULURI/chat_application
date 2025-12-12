# cmail.py — defensive Brevo sender with diagnostics
import os
import requests
import json
import traceback
from typing import Any

BREVO_API_KEY = os.environ.get("BREVO_API_KEY")  # load once

def _safe_str(x: Any) -> str:
    """Convert value to a readable string for email bodies (avoid trying to JSON-serialize complex objects)."""
    if x is None:
        return ""
    if isinstance(x, (str, bytes)):
        return x.decode('utf-8') if isinstance(x, bytes) else x
    # For lists/dicts, produce a readable text summary (not JSON) to avoid recursion
    try:
        return str(x)
    except Exception:
        return repr(x)

def _is_serializable(obj) -> bool:
    """Quick check to see if json.dumps will work without raising RecursionError or TypeError."""
    try:
        # Use a shallow dumps with default=str (so uncommon types don't break)
        json.dumps(obj, default=str)
        return True
    except RecursionError:
        return False
    except Exception:
        # other errors like TypeError are OK to return False
        return False

def send_email(to: str, subject: str, body: Any) -> bool:
    """
    Send a plain-text email via Brevo.
    Returns True on success (201), False on any error.
    This function is defensive: it will coerce/validate inputs and log full tracebacks.
    """
    if not BREVO_API_KEY:
        # Production: use app.logger instead of print; kept print for immediate Render logs
        print("BREVO_API_KEY missing")
        return False

    # Ensure minimal string types for payload fields
    try:
        to_str = _safe_str(to)
        subject_str = _safe_str(subject)
        # If body is not a string, convert to a safe string (prevents json recursion)
        if isinstance(body, str):
            body_str = body
        else:
            # If it's a dict/list, convert to readable text instead of JSON structure
            # This avoids circular references that cause RecursionError during json.dumps(payload)
            body_str = _safe_str(body)
    except Exception:
        print("Error coercing email fields:")
        traceback.print_exc()
        return False

    payload = {
        "sender": {"name": "Chat Application", "email": "yogendrakavuluri8@gmail.com"},
        "to": [{"email": to_str}],
        "subject": subject_str,
        "textContent": body_str
    }

    # Diagnostic: check serializability of the payload before sending
    if not _is_serializable(payload):
        print("Email payload is not JSON-serializable (likely circular). Dumping diagnostics:")
        try:
            # Show types and repr of suspicious fields
            print("type(to):", type(to))
            print("type(subject):", type(subject))
            print("type(body):", type(body))
            print("repr(body) (first 1000 chars):", repr(body)[:1000])
        except Exception:
            pass
        return False

    try:
        resp = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            headers={"api-key": BREVO_API_KEY, "Content-Type": "application/json"},
            json=payload,
            timeout=10
        )
    except RecursionError:
        print("Brevo request failed: RecursionError while serializing payload")
        traceback.print_exc()
        return False
    except Exception:
        print("Brevo request failed (exception):")
        traceback.print_exc()
        return False

    # success code according to Brevo is 201 Created
    if resp.status_code == 201:
        return True
    else:
        print("Brevo email returned non-201:", resp.status_code, resp.text[:200])
        return False
