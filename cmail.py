import os
from mailersend import MailerSend

def send_email(to, subject, body):
    try:
        mailer = MailerSend(api_key=os.environ["MAILERSEND_API_KEY"])

        mailer.email.send(
            {
                "from": {
                    "email": "noreply@mailersend.net",
                    "name": "Chat App"
                },
                "to": [
                    {"email": to}
                ],
                "subject": subject,
                "text": body
            }
        )

        print("Mail sent successfully")
        return True

    except Exception as e:
        print("Mailersend error:", e)
        return False
