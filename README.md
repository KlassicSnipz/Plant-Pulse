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