from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv
import os
import json
import logging
import pulsar

# Cargar variables .env
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("email-api")

PULSAR_URL = os.getenv("PULSAR_URL")
EMAIL_TOPIC = os.getenv("EMAIL_TOPIC")

client = pulsar.Client(PULSAR_URL)

app = FastAPI(title="Email Notification Microservice")

class EmailPayload(BaseModel):
    to: EmailStr
    subject: str
    body: str
    html: bool = False

@app.get("/health")
def health():
    return {"status": "ok"}

def publish_email(payload: dict):
    producer = client.create_producer(EMAIL_TOPIC)
    producer.send(json.dumps(payload).encode("utf-8"))
    producer.close()
    logger.info("Email enviado a cola Pulsar")

@app.post("/send-email")
def send_email(payload: EmailPayload, background_tasks: BackgroundTasks):
    background_tasks.add_task(publish_email, payload.dict())
    return {"message": "Email encolado correctamente"}
