import json
import random
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

from devices import DEVICES, READING_TYPES

INTERVAL = 5
BAD_RATE = 0.015
MEAN_REVERSION = 0.05


#MQTT broker connection
#-------------------------------------------------------------------------------
BROKER_HOST = "localhost"
BROKER_PORT = 1883

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect(BROKER_HOST, BROKER_PORT)
client.loop_start()
#-------------------------------------------------------------------------------

state = {}
for device in DEVICES:
    for reading_type in device["reading_types"]:
        spec = READING_TYPES[reading_type]
        centre = (spec["low"] + spec["high"]) / 2
        span = spec["high"] - spec["low"]
        state[(device["device_id"], reading_type)] = centre + random.uniform(-0.15, 0.15) * span


def next_value(current, reading_type):
    spec = READING_TYPES[reading_type]
    span = spec["high"] - spec["low"]
    centre = (spec["low"] + spec["high"]) / 2
    drift = random.gauss(0, spec["step"] * span)
    pull = (centre - current) * MEAN_REVERSION
    value = current + drift + pull
    return max(spec["low"], min(spec["high"], value))


def build_reading(device, reading_type, value):
    return {
        "device_id": device["device_id"],
        "zone": device["zone"],
        "reading_type": reading_type,
        "value": round(value, 2),
        "unit": READING_TYPES[reading_type]["unit"],
        "ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
    }


def corrupt(reading):
    kind = random.choice(["out_of_range", "missing_field", "malformed_value"])
    broken = dict(reading)

    if kind == "out_of_range":
        spec = READING_TYPES[reading["reading_type"]]
        span = spec["high"] - spec["low"]
        if random.random() < 0.5:
            broken["value"] = round(spec["high"] + span * random.uniform(1.0, 3.0), 2)
        else:
            broken["value"] = round(spec["low"] - span * random.uniform(0.5, 1.5), 2)
    elif kind == "missing_field":
        broken.pop(random.choice(["value", "unit", "ts"]), None)
    else:
        broken["value"] = random.choice(["NaN", "N/A", "", "ERR"])

    return broken


print("Running simulator...")
while True:
    for device in DEVICES:
        for reading_type in device["reading_types"]:
            key = (device["device_id"], reading_type)
            state[key] = next_value(state[key], reading_type)
            reading = build_reading(device, reading_type, state[key])

            if random.random() < BAD_RATE:
                reading = corrupt(reading)

            topic = f"plant/{device['zone']}/{device['device_id']}/{reading_type}"
            payload = json.dumps(reading)
            #Send reading to MQTT broker
            client.publish(topic, payload, qos=1)

    time.sleep(INTERVAL)