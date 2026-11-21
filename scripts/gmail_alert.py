import os
import smtplib
from email.message import EmailMessage


def send_gmail(subject, body):
    sender = os.environ.get("GMAIL_SENDER", "").strip()
    recipient = os.environ.get("GMAIL_RECIPIENT", "").strip()
    app_password = os.environ.get("GMAIL_APP_PASSWORD", "").replace(" ", "")

    if not sender or not recipient or not app_password:
        print("Gmail is not configured; email alert was not sent.")
        return False

    message = EmailMessage()
    message["From"] = sender
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as server:
            server.login(sender, app_password)
            server.send_message(message)
        print("Gmail alert sent successfully.")
        return True
    except Exception as error:
        print(f"Gmail alert could not be sent: {error}")
        return False
