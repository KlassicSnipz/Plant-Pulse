# simulator

Generates synthetic sensor readings for the plant and publishes them over MQTT.

## What it does

Walks a list of 20 devices (pumps, valves, compressors, flowmeters, tanks,
export pumps), and for each device's reading types, computes a plausible
next value and publishes it to the MQTT broker. Runs forever — one full
pass over every device every `INTERVAL` seconds.

## Files

- `main.py` — the simulation loop and MQTT publishing
- `devices.py` — `DEVICES` (the 20-device inventory) and `READING_TYPES`
  (unit/low/high/step per reading type)
- `Dockerfile`, `requirements.txt`

## How values are generated

Each device/reading_type pair keeps a `state` value in memory, primed once
at startup to a random point near the center of its normal range. On every
pass through the main loop:

1. `next_value()` drifts the current value using `random.gauss` noise
   scaled by `step`, then pulls it back toward the center of its range
   (`MEAN_REVERSION`) so it never wanders off indefinitely. The result is
   clamped to `[low, high]`.
2. `build_reading()` packages the value into the JSON shape every
   downstream service expects: `device_id`, `zone`, `reading_type`,
   `value`, `unit`, `ts`.
3. `corrupt()` runs about 1.5% of the time (`BAD_RATE`), deliberately
   breaking the reading one of three ways — pushing the value out of
   range, deleting a field, or replacing the value with a bogus string —
   so the validation logic downstream (in `consumer/`) has real bad data
   to catch.

## Publishing

Each reading is published to `plant/<zone>/<device_id>/<reading_type>`
with QoS 1.

## Config (environment variables)

| Variable | Default | Purpose |
|---|---|---|
| `BROKER_HOST` | `localhost` | MQTT broker hostname |
| `BROKER_PORT` | `1883` | MQTT broker port |

Also set directly in `main.py`: `INTERVAL` (5s between passes), `BAD_RATE`
(1.5%), `MEAN_REVERSION` (0.05).

## Running standalone

Normally started as part of the full pipeline
(`docker compose up -d --build` from the project root). To run it directly:

```
cd simulator
pip install -r requirements.txt
python main.py
```

Requires a reachable MQTT broker at `BROKER_HOST:BROKER_PORT`.
