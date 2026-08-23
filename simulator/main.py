"""Plant Pulse sensor simulator — stage 1: print readings to stdout.

Generates synthetic industrial telemetry for the plant described in
docs/DECISIONS.md. No MQTT yet: this stage exists so the generated data can be
inspected on its own, before any broker, container, or database is involved.

Values follow a random walk with mild mean reversion, so each stream drifts
around a setpoint the way a real sensor does instead of jumping randomly
between readings.

A small fraction of readings is corrupted on purpose (--bad-rate). Without
bad data, the validation and quality layers later in the pipeline would never
have anything real to catch.

Usage:
    python main.py                       # run forever, all zones
    python main.py --limit 20            # emit 20 readings and stop
    python main.py --zone zone-1         # only Zone 1 devices
    python main.py --seed 42             # reproducible output
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
from datetime import datetime, timezone

from devices import DEVICES, READING_TYPES, streams

# How strongly a value is pulled back toward the middle of its normal band.
# 0 = pure random walk (wanders off), 1 = snaps to centre (no drift at all).
MEAN_REVERSION = 0.05

# The three ways a reading can be deliberately broken.
CORRUPTIONS = ("out_of_range", "missing_field", "malformed_value")


def utc_now() -> str:
    """Current time as an ISO 8601 UTC string, e.g. 2026-08-23T10:15:03.412Z."""
    return (
        datetime.now(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


def initial_value(reading_type: str, rng: random.Random) -> float:
    """Pick a plausible starting point near the middle of the normal band."""
    spec = READING_TYPES[reading_type]
    centre = (spec["low"] + spec["high"]) / 2
    span = spec["high"] - spec["low"]
    return centre + rng.uniform(-0.15, 0.15) * span


def next_value(current: float, reading_type: str, rng: random.Random) -> float:
    """Advance one step of the random walk for a single stream.

    Two forces combine: a small random nudge (the drift), and a gentle pull
    back toward the centre of the normal band (the mean reversion) so the
    value does not wander out of range over a long run.
    """
    spec = READING_TYPES[reading_type]
    span = spec["high"] - spec["low"]
    centre = (spec["low"] + spec["high"]) / 2

    drift = rng.gauss(0, spec["step"] * span)
    pull = (centre - current) * MEAN_REVERSION
    value = current + drift + pull

    # Keep normal readings inside the normal band; out-of-range values are
    # produced deliberately by corrupt(), never by accident here.
    return max(spec["low"], min(spec["high"], value))


def build_reading(device: dict, reading_type: str, value: float) -> dict:
    """Assemble one reading as a plain Python dict.

    The dict is the working form; it becomes JSON only at the moment it is
    emitted. That is why nothing here touches the json module.
    """
    return {
        "device_id": device["device_id"],
        "zone": device["zone"],
        "reading_type": reading_type,
        "value": round(value, 2),
        "unit": READING_TYPES[reading_type]["unit"],
        "ts": utc_now(),
    }


def corrupt(reading: dict, rng: random.Random) -> dict:
    """Return a deliberately broken variant of a reading.

    Each corruption mirrors a real failure mode: a sensor reporting a wild
    value, a firmware bug dropping a field, or a device sending a status
    string where a number belongs.
    """
    broken = dict(reading)
    kind = rng.choice(CORRUPTIONS)

    if kind == "out_of_range":
        spec = READING_TYPES[reading["reading_type"]]
        span = spec["high"] - spec["low"]
        if rng.random() < 0.5:
            broken["value"] = round(spec["high"] + span * rng.uniform(1.0, 3.0), 2)
        else:
            broken["value"] = round(spec["low"] - span * rng.uniform(0.5, 1.5), 2)

    elif kind == "missing_field":
        broken.pop(rng.choice(["value", "unit", "ts"]), None)

    elif kind == "malformed_value":
        broken["value"] = rng.choice(["NaN", "N/A", "", "ERR"])

    return broken


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate synthetic plant telemetry and print it as JSON lines."
    )
    parser.add_argument(
        "--interval", type=float, default=5.0,
        help="seconds between reading cycles (default: 5.0)",
    )
    parser.add_argument(
        "--limit", type=int, default=0,
        help="stop after this many readings; 0 means run forever (default: 0)",
    )
    parser.add_argument(
        "--bad-rate", type=float, default=0.015,
        help="fraction of readings to corrupt on purpose (default: 0.015)",
    )
    parser.add_argument(
        "--zone", default=None,
        help="only emit readings for this zone, e.g. zone-1 (default: all zones)",
    )
    parser.add_argument(
        "--seed", type=int, default=None,
        help="random seed, for reproducible output (default: random)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    rng = random.Random(args.seed)

    selected = [
        (device, reading_type)
        for device, reading_type in streams()
        if args.zone is None or device["zone"] == args.zone
    ]
    if not selected:
        known = sorted({d["zone"] for d in DEVICES})
        print(f"No devices in zone {args.zone!r}. Known zones: {known}", file=sys.stderr)
        return 1

    # One current value per stream. This is the simulator's entire memory:
    # it never grows, because each new value replaces the previous one.
    state = {
        (device["device_id"], reading_type): initial_value(reading_type, rng)
        for device, reading_type in selected
    }

    print(
        f"Simulating {len(selected)} streams across "
        f"{len({d['zone'] for d, _ in selected})} zone(s), "
        f"every {args.interval}s. Ctrl-C to stop.",
        file=sys.stderr,
    )

    emitted = 0
    try:
        while True:
            for device, reading_type in selected:
                key = (device["device_id"], reading_type)
                state[key] = next_value(state[key], reading_type, rng)
                reading = build_reading(device, reading_type, state[key])

                if rng.random() < args.bad_rate:
                    reading = corrupt(reading, rng)

                print(json.dumps(reading), flush=True)
                emitted += 1

                if args.limit and emitted >= args.limit:
                    return 0

            time.sleep(args.interval)
    except KeyboardInterrupt:
        print(f"\nStopped after {emitted} readings.", file=sys.stderr)
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
