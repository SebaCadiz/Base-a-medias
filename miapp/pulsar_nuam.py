
from pulsar import Client
import json
from .models import Evento
# Importamos os para usar la variable de entorno
import os

# Obtener la URL de Pulsar desde las variables de entorno para usarla aquí
PULSAR_URL = os.getenv("PULSAR_URL", "pulsar://localhost:6650")
DEFAULT_TOPIC = "eventos-usuarios"


def enmascarar_datos(data):
    data_segura = data.copy() 
    campos_sensibles = ['mail', 'usuario_id', 'contraseña', 'monto', 'nombre', 'apellido']
    
    for key in data_segura:
        if key in campos_sensibles:
            valor_original = str(data_segura[key])
            if len(valor_original) > 2:
                data_segura[key] = valor_original[:2] + "****"
            else:
                data_segura[key] = "****"
                
    return data_segura

def publicar_evento(tipo, data, topic=DEFAULT_TOPIC): # <-- **AÑADIMOS el argumento 'topic'**
    try:
        # Usamos la variable de entorno
        client = Client(PULSAR_URL) 
        # Usamos el tópico que recibimos (por defecto, eventos-usuarios)
        producer = client.create_producer(topic) 

        mensaje = {"tipo": tipo, "data": data}
        
        # Si el tópico es el de correo, el payload es el email_payload directamente.
        # En caso contrario, usamos el formato de Evento.
        if topic != os.getenv("EMAIL_TOPIC"):
            # Si no es el tópico de correo, enviamos el mensaje estructurado con "tipo" y "data"
            producer.send(json.dumps(mensaje).encode('utf-8'))
        else:
            # Si es el tópico de correo, 'data' ya es el payload de correo (to, subject, body),
            # así que lo enviamos directamente. El 'worker.py' espera solo ese payload.
            producer.send(json.dumps(data).encode('utf-8'))


        print(f"Mensaje enviado a Pulsar (Tópico: {topic}):", mensaje if topic != os.getenv("EMAIL_TOPIC") else data)
        contenido_seguro = enmascarar_datos(data)

        # Solo registramos eventos en la tabla si no es el tópico de correo (opcional, pero limpio)
        if topic != os.getenv("EMAIL_TOPIC"):
            Evento.objects.create(
                tipo=tipo,
                contenido=contenido_seguro
            )

        client.close() 

    except Exception as e:
        print(f"⚠️ No se pudo conectar a Pulsar (Tópico: {topic}):", str(e))
        
        # En caso de fallo de conexión a Pulsar, aún guardamos el Evento en DB si no es un correo
        if topic != os.getenv("EMAIL_TOPIC"):
            contenido_seguro = enmascarar_datos(data)
            Evento.objects.create(
                tipo=tipo,
                contenido=contenido_seguro
            )