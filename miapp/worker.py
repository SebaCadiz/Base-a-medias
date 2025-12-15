from dotenv import load_dotenv
load_dotenv()
import os
import json
import logging
import smtplib
from email.message import EmailMessage
import pulsar

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("email-worker")

PULSAR_URL = os.getenv("PULSAR_URL")
EMAIL_TOPIC = os.getenv("EMAIL_TOPIC")

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
DEFAULT_FROM = os.getenv("DEFAULT_NOTIFICATION_EMAIL")

def send_email(data: dict):
    msg = EmailMessage()
    msg["From"] = DEFAULT_FROM
    msg["To"] = data["to"]
    msg["Subject"] = data["subject"]

    if data.get("html"):
        msg.add_alternative(data["body"], subtype="html")
    else:
        msg.set_content(data["body"])

    server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
    server.starttls()
    server.login(SMTP_USER, SMTP_PASS)
    server.send_message(msg)
    server.quit()

    logger.info("Email enviado a %s", data["to"])

def main():
    client = pulsar.Client(PULSAR_URL)
    consumer = client.subscribe(EMAIL_TOPIC, "email-subscription")

    logger.info("Worker escuchando Pulsar...")

    while True:
        msg = consumer.receive()
        data = json.loads(msg.data().decode())
        try:
            send_email(data)
            consumer.acknowledge(msg)
        except Exception as e:
            logger.error("Error enviando email: %s", e)
            consumer.negative_acknowledge(msg)

if __name__ == "__main__":
    main()
