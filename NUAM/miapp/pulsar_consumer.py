from pulsar import Client, ConsumerType
import json

client = Client("pulsar://pulsar:6650")  # nombre del servicio Docker

consumer = client.subscribe(
    "eventos-usuarios",
    "mi-suscripcion",
    consumer_type=ConsumerType.Shared
)

print("Esperando mensajes de Pulsar...")

while True:
    msg = consumer.receive()
    data = json.loads(msg.data().decode("utf-8"))
    print("Mensaje recibido:", data)
    consumer.acknowledge(msg)
