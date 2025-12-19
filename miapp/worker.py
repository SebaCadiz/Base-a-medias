from dotenv import load_dotenv
load_dotenv()
import os
import json
import logging
import smtplib
from email.message import EmailMessage
import pulsar
import ast  # nuevo import para fallback parsing

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
    
    # Manejo de destinatarios
    to_field = data.get("to")
    msg["To"] = ", ".join(map(str, to_field)) if isinstance(to_field, (list, tuple)) else str(to_field)
    msg["Subject"] = data.get("subject", "")

    if data.get("html"):
        msg.add_alternative(data.get("body", ""), subtype="html")
    else:
        msg.set_content(data.get("body", ""))

    # --- MEJORA DE ESTABILIDAD ---
    try:
        # Añadimos un timeout para evitar que el worker se quede colgado
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
            server.set_debuglevel(1)  # Activa esto para ver el diálogo exacto en la terminal
            server.ehlo()            # Identificación inicial obligatoria
            server.starttls()        # Cifrado
            server.ehlo()            # Re-identificación tras cifrado
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
            logger.info("Email enviado exitosamente a %s", msg["To"])
    except smtplib.SMTPException as e:
        logger.error("Error específico de SMTP: %s", e)
        raise

def _parse_message_bytes(raw_bytes):
    # intenta varias formas de parsing para aceptar distintos formatos
    try:
        decoded = raw_bytes.decode("utf-8")
    except Exception:
        decoded = None

    logger.debug("Raw message bytes: %s", raw_bytes)
    if decoded is not None:
        logger.info("Mensaje recibido (decoded): %s", decoded)

        # intento normal json
        try:
            return json.loads(decoded)
        except Exception:
            pass

        # si es string con JSON dentro (doble-serializado)
        try:
            inner = json.loads(decoded.strip('"'))
            if isinstance(inner, (dict, list)):
                return inner
        except Exception:
            pass

        # fallback a literal_eval para objetos con comillas simples
        try:
            return ast.literal_eval(decoded)
        except Exception:
            pass

    # último recurso: intentar json.loads directamente de bytes
    try:
        return json.loads(raw_bytes)
    except Exception:
        return None

def _find_payload_with_keys(obj, required_keys):
    """
    Busca recursivamente un dict que contenga todas las required_keys.
    """
    if isinstance(obj, dict):
        if all(k in obj for k in required_keys):
            return obj
        for v in obj.values():
            found = _find_payload_with_keys(v, required_keys)
            if found:
                return found
    elif isinstance(obj, (list, tuple)):
        for item in obj:
            found = _find_payload_with_keys(item, required_keys)
            if found:
                return found
    return None

def main():
    client = pulsar.Client(PULSAR_URL)
    consumer = client.subscribe(EMAIL_TOPIC, "email-subscription")

    logger.info("Worker escuchando Pulsar...")

    while True:
        msg = consumer.receive()
        raw = msg.data()
        data = _parse_message_bytes(raw)

        logger.debug("Parsed message type: %s, content: %s", type(data), data)

        if data is None:
            logger.error("No se pudo parsear el mensaje: %s", raw)
            # ACK para evitar reintentos infinitos de mensajes inválidos
            consumer.acknowledge(msg)
            continue

        # Si no contiene las claves necesarias, buscar recursivamente un payload válido
        required = ("to", "subject", "body")
        if not (isinstance(data, dict) and all(k in data for k in required)):
            found = _find_payload_with_keys(data, required)
            if found:
                data = found
            else:
                logger.error("Mensaje inválido, no contiene 'to/subject/body'. Data: %s", data)
                # ACK para evitar reentrega continua de mensajes malformados
                consumer.acknowledge(msg)
                continue

        # validar campos requeridos (ahora deberían existir)
        missing = [k for k in required if k not in data]
        if missing:
            logger.error("Mensaje inválido, faltan campos: %s. Data: %s", missing, data)
            consumer.acknowledge(msg)
            continue

        try:
            send_email(data)
            consumer.acknowledge(msg)
        except Exception as e:
            logger.error("Error enviando email: %s", e)
            # si ocurre error en envío, negative_ack para reintento
            consumer.negative_acknowledge(msg)

if __name__ == "__main__":
    main()

