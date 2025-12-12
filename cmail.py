from mailersend import emails
import os

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

        mailer.send(mail_body)
        print("Mailersend success")
        return True

    except Exception as e:
        print("Mailersend error:", e)
        return False
