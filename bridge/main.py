import paho.mqtt.client as mqtt
from kafka import KafkaProducer

MQTT_BROKER_HOST = "localhost"
MQTT_BROKER_PORT = 1883
MQTT_TOPIC_FILTER = "plant/#"

KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
KAFKA_TOPIC = "plant.readings.raw"

producer = KafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)


def on_connect(client, userdata, flags, reason_code, properties):
    print(f"connected to MQTT broker (reason_code={reason_code}), subscribing to {MQTT_TOPIC_FILTER}")
    client.subscribe(MQTT_TOPIC_FILTER, qos=1)


def on_message(client, userdata, message):
    key = message.topic.encode("utf-8")
    value = message.payload

    producer.send(KAFKA_TOPIC, key=key, value=value)
    print(f"{message.topic} -> kafka:{KAFKA_TOPIC}  {value}")


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT)
client.loop_forever()