# Plant Pulse

Industrial telemetry pipeline: simulated plant sensors publish over MQTT, a
bridge forwards readings into Kafka, a Python consumer validates and lands
them in PostgreSQL, dbt builds a star schema on top, Airflow runs the batch
transform/quality checks on an hourly schedule, and Power BI serves the
result.

## Status

Just started — building incrementally, one working slice at a time. See
commit history for progress.

## Stack

Python · MQTT (Mosquitto) · Kafka · PostgreSQL · dbt · Airflow ·
Great Expectations · Docker Compose · Power BI
