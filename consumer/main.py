import json

import psycopg2
from kafka import KafkaConsumer

KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
KAFKA_TOPIC = "plant.readings.raw"
KAFKA_GROUP_ID = "postgres-writer"

PG_DSN = "host=localhost port=5434 dbname=plant_pulse user=plant_pulse password=plant_pulse"

READING_RANGES = {
    "temperature": (40.0, 90.0),
    "pressure": (1.0, 10.0),
    "vibration": (0.0, 15.0),
    "flow": (0.0, 500.0),
}

INSERT_SQL = """
    INSERT INTO raw_readings (device_id, zone, reading_type, value, unit, reading_ts, quality_flag)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
"""


def validate(reading):
    if "value" not in reading or "unit" not in reading or "ts" not in reading:
        return reading.get("value"), "missing_field"

    try:
        value = float(reading["value"])
    except (TypeError, ValueError):
        return None, "malformed_value"

    low, high = READING_RANGES.get(reading.get("reading_type"), (None, None))
    if low is not None and not (low <= value <= high):
        return value, "out_of_range"

    return value, "ok"


def main():
    conn = psycopg2.connect(PG_DSN)
    conn.autocommit = True
    cur = conn.cursor()

    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=KAFKA_GROUP_ID,
        auto_offset_reset="earliest",
    )

    print(f"listening on kafka topic '{KAFKA_TOPIC}', writing into raw_readings...")

    for message in consumer:
        try:
            reading = json.loads(message.value)
        except (json.JSONDecodeError, TypeError):
            cur.execute(INSERT_SQL, (None, None, None, None, None, None, "unparseable"))
            print("unparseable message -> quality_flag='unparseable'")
            continue

        value, quality_flag = validate(reading)

        cur.execute(INSERT_SQL, (
            reading.get("device_id"),
            reading.get("zone"),
            reading.get("reading_type"),
            value,
            reading.get("unit"),
            reading.get("ts"),
            quality_flag,
        ))
        print(f"{reading.get('device_id')} {reading.get('reading_type')} -> quality_flag='{quality_flag}'")


if __name__ == "__main__":
    main()