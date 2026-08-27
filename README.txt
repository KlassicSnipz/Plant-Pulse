# Plant Pulse

Industrial telemetry pipeline: simulated plant sensors publish over MQTT, a
bridge forwards readings into Kafka, a Python consumer validates and lands
them in PostgreSQL, dbt builds a star schema on top, Airflow runs the batch
transform/quality checks on an hourly schedule, and Power BI serves the
result.

## Stack

Python · MQTT (Mosquitto) · Kafka · PostgreSQL · dbt · Airflow · Power BI

## Devices

Device Reading types:
   - Pump: [temperature, vibration]
   - Valve: [pressure, flow]
   - Compressor: [temperature, pressure, vibration]
   - Flowmeter: [flow]
   - Tank: [temperature, pressure]
   - Export pump: [temperature, vibration, pressure]

Reading types:
   - temperature: °C
   - pressure: bar
   - vibration: mm/s
   - flow: m³/h

## Running

Current milestone: the simulator generates synthetic sensor readings and
publishes them over MQTT to a Mosquitto broker. Kafka, Postgres, dbt, and
Airflow aren't wired in yet — this section will grow as each one comes
online.

Requires Docker Desktop running, and Python 3.11+.


## 1. Start the broker

docker compose up -d
docker compose ps

`mosquitto` should show as running.

## 2. Watch for messages (second terminal)

docker compose exec mosquitto mosquitto_sub -h localhost -t "plant/#" -v


## 3. Start the simulator (third terminal)

cd simulator
pip install -r requirements.txt
python main.py

Matching lines should appear in both the simulator window and the
subscriber window within a few seconds — that confirms messages are
actually reaching the broker, not just that the script ran.


##4. Stop everything

docker compose down
