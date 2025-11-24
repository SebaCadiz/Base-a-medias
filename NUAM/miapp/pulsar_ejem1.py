from pulsar import Client
import json

# Conecta con el broker Pulsar (el que levantaste en Docker)
client = Client("pulsar://localhost:6650")

# Crea un "productor" para el topic "eventos-usuarios"
producer = client.create_producer("eventos-usuarios")

# Función para publicar un evento
def publicar_evento(data):
    mensaje = json.dumps(data)          # Convierte el diccionario a JSON
    producer.send(mensaje.encode('utf-8'))  # Envía el mensaje al topic
