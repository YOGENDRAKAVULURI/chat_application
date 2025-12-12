from mailersend import emails

def send_mail(to_email, otp):
    mailer = emails.NewEmail(api_key=os.environ["MAILERSEND_API_KEY"])

    mail_body = {
        "from": {"email": "your_verified@mail.com", "name": "Chat App"},
        "to": [{"email": to_email}],
        "subject": "Your OTP Code",
        "text": f"Your OTP is: {otp}"
    }

    try:
        response = mailer.send(mail_body)
        print("Email sent:", response)
        return True
    except Exception as e:
        print("MailerSend Failed:", e)
        return False
