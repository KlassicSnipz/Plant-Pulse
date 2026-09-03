# Plant Pulse

Industrial telemetry pipeline, built end to end to learn the stack: simulated
plant sensors publish readings over MQTT, a bridge forwards them into Kafka,
a Python consumer validates and lands them in PostgreSQL, and dbt transforms
the raw data into a proper star schema. Airflow will orchestrate the
transform on a schedule, and Power BI will serve the result — both planned,
not yet built.

```
simulator --(MQTT)--> mosquitto --(bridge)--> kafka --(consumer)--> postgres --(dbt)--> star schema
```

## Stack

Python · MQTT (Mosquitto) · Kafka (KRaft) · PostgreSQL · Docker Compose · dbt · Airflow (planned) · Power BI (planned)


## Devices

Device reading types:
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

## Project structure

```
Plant-Pulse/
  docker-compose.yml
  sql/ddl/raw_readings.sql       DDL for the raw ingestion table
  simulator/                     generates and publishes synthetic readings over MQTT
  bridge/                        forwards MQTT readings into Kafka, unchanged
  consumer/                      validates Kafka messages and inserts into raw_readings
  mosquitto/mosquitto.conf
  dbt_plant/                     dbt project: raw_readings -> staging -> star schema
  docs/DECISIONS.md              architecture decision log
```

## Running the pipeline

Requires Docker Desktop running.

Bring up the full stack — Mosquitto, Postgres, Kafka, simulator, bridge, and
consumer — with one command:

```
docker compose up -d --build
docker compose ps
```

All six services should show as `Up`. `simulator`, `bridge`, and `consumer`
may restart once or twice right after startup while Kafka finishes booting —
that's expected, not a failure.

Watch what a service is doing:

```
docker compose logs -f simulator
docker compose logs -f bridge
docker compose logs -f consumer
```

Watch MQTT traffic directly:

```
docker compose exec mosquitto mosquitto_sub -h localhost -t "plant/#" -v
```

Watch Kafka traffic directly:

```
docker compose exec kafka /opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic plant.readings.raw --from-beginning
```

Check row count, or connect with a client (DBeaver: host `localhost`, port
`5434`, db/user/password all `plant_pulse`):

```
docker compose exec postgres psql -U plant_pulse -d plant_pulse -c "SELECT count(*) FROM raw_readings;"
```

Stop everything (data persists):

```
docker compose down
```

Stop everything and wipe Postgres data (forces the DDL to re-run on next `up`):

```
docker compose down -v
```

## dbt — star schema

The `dbt_plant/` project builds a star schema on top of `raw_readings`:
`stg_raw_readings` (staging, cleaned/typed) feeds five mart models —
`dim_device`, `dim_zone`, `dim_reading`, `dim_quality`, and `fact_readings`
— all landing in the `analytics` schema. Every model has tests (uniqueness,
not-null, and foreign-key relationship checks) and descriptions defined in
`schema.yml` files.

dbt is a batch tool, not a streaming one — it only reflects whatever's in
`raw_readings` at the moment you run it. Run it again any time you want the
star schema to catch up with new data.

**Containerized (no manual install needed)** — `docker compose up -d --build`
already builds the `dbt` image from `dbt_plant/requirements.txt`, so a fresh
`git clone` needs nothing extra installed to run this. Whenever you want to
refresh the star schema from whatever's currently in `raw_readings`:

```
docker compose run --rm dbt build
```

Run tests on their own, without rebuilding:

```
docker compose run --rm dbt test
```

**Local (optional, for active development)** — only useful if you're
iterating on the models themselves and want faster feedback than rebuilding
a Docker image each time. Requires `dbt-postgres` installed locally
(`uv pip install dbt-postgres`):

```
cd dbt_plant
dbt build
```

Generate and browse the docs site (model descriptions + lineage graph) —
this one needs a local dbt install either way, since `dbt docs serve` opens
a browser-facing local web server that doesn't make sense to run inside a
container:

```
cd dbt_plant
dbt docs generate
dbt docs serve
```

## Roadmap

- **Airflow** — orchestrate the dbt build on a schedule (hourly), replacing
  the manual `dbt build` step.
- **Power BI** — connect to the `analytics` schema and build reports on top
  of `fact_readings`.