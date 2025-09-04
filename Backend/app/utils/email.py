import smtplib
from email.mime.text import MIMEText
from app.core.config import env

SMTP_HOST = env("SMTP_HOST")
SMTP_PORT = env("SMTP_PORT", int)
SMTP_USER = env("SMTP_USER")
SMTP_PASSWORD = env("SMTP_PASSWORD")
SMTP_SENDER = env("SMTP_SENDER")

def send_verification_email(to_email: str, code: str):
    subject = "Votre code de vérification JEB Incubator"
    body = f"Votre code de vérification est : {code}\nCe code est valable 10 minutes."
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SMTP_SENDER
    msg["To"] = to_email

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_SENDER, [to_email], msg.as_string())
