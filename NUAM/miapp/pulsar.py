from pulsar import Client
import json
from miapp.models import Evento

def publicar_evento(tipo, data):
    try:
        # Conectar a Pulsar
        client = Client("pulsar://localhost:6650")
        producer = client.create_producer("eventos-usuarios")

        mensaje = {"tipo": tipo, "data": data}

        producer.send(json.dumps(mensaje).encode('utf-8'))
        print("Mensaje enviado a Pulsar:", mensaje)

        # Guardar evento en Django
        Evento.objects.create(
            tipo=tipo,
            contenido=data
        )

        client.close()  # Cerrar conexión después de enviar

    except Exception as e:
        print("⚠️ No se pudo conectar a Pulsar:", str(e))
