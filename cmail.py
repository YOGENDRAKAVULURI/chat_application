import os
import smtplib
from email.message import EmailMessage

def send_email(to, subject, body):
    smtp_user = os.environ.get("SMTP_USER")
    smtp_pass = os.environ.get("SMTP_PASSWORD")

    if not smtp_user or not smtp_pass:
        raise RuntimeError("SMTP_USER or SMTP_PASSWORD not set in environment")

    # ✅ use Gmail with STARTTLS and timeout so it works on Render
    with smtplib.SMTP("smtp.gmail.com", 587, timeout=10) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)

        msg = EmailMessage()
        msg['From'] = smtp_user
        msg['To'] = to
        msg['Subject'] = subject
        msg.set_content(body)

        server.send_message(msg)
