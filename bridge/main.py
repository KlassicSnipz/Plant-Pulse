"""
MQTT -> Kafka bridge.

Subscribes to every reading published under plant/# on the Mosquitto broker
and republishes each message, unchanged, onto a single Kafka topic. This is
the seam between "device transport" (MQTT, lightweight, fire-and-forget) and
"pipeline transport" (Kafka, durable, replayable) -- the bridge does no
validation and no reshaping. That happens downstream, in the consumer that
writes into raw_readings. If the bridge started fixing or dropping bad
messages, raw_readings would stop being a true record of what devices sent.
"""

import os

import paho.mqtt.client as mqtt
from kafka import KafkaProducer

MQTT_BROKER_HOST = os.environ.get("MQTT_BROKER_HOST", "localhost")
MQTT_BROKER_PORT = int(os.environ.get("MQTT_BROKER_PORT", "1883"))
MQTT_TOPIC_FILTER = "plant/#"

KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC = "plant.readings.raw"

producer = KafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)


def on_connect(client, userdata, flags, reason_code, properties):
    print(f"connected to MQTT broker (reason_code={reason_code}), subscribing to {MQTT_TOPIC_FILTER}")
    client.subscribe(MQTT_TOPIC_FILTER, qos=1)


def on_message(client, userdata, message):
    # message.topic looks like: plant/zone-1/pump-01/temperature
    key = message.topic.encode("utf-8")
    value = message.payload  # forwarded as-is: whatever bytes MQTT delivered

    producer.send(KAFKA_TOPIC, key=key, value=value)
    print(f"{message.topic} -> kafka:{KAFKA_TOPIC}  {value}")


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT)
client.loop_forever()