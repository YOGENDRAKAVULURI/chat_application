import os
from mailersend import emails

def send_email(to, subject, body):
    try:
        mailer = emails.NewEmail(os.environ["MAILERSEND_API_KEY"])

        mail_body = {
            "from": {
                "email": "noreply@mailersend.net",
                "name": "Chat App"
            },
            "to": [
                {
                    "email": to
                }
            ],
            "subject": subject,
            "text": body
        }

        response = mailer.send(mail_body)
        print("Mail sent:", response)
        return True

    except Exception as e:
        print("Send mail failed:", e)
        return False
