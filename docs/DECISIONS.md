# Decisions

One entry per real choice, added as the choice gets made — not written after the fact.

## 2026-08-22 — Zone layout mirrors a real process flow

The plant is split into 3 zones that follow an actual process order rather
than being an arbitrary bucket for devices: intake/pumping feeds into
processing/compression, which feeds into storage/distribution. This gives
`Dim_Zone` a real hierarchy to describe later, and makes it possible to ask
realistic questions of the data (e.g. "does Zone 1 vibration correlate with
Zone 2 pressure a few minutes later").

## 2026-08-22 — Devices report only the reading types that make physical sense

Not every device emits all four reading types. Devices with moving parts
(pumps, compressors) report vibration; devices without (valves, flow
meters, tanks) don't. This is what gives the device-to-reading-type
relationship meaning, instead of `Dim_ReadingType` being decorative.

## 2026-08-22 — Device inventory (20 devices, 3 zones)

**Zone 1 — Intake & Pumping** (7 devices)

| Device ID | Type | Reports |
|---|---|---|
| `pump-01` | Centrifugal pump | temperature, vibration |
| `pump-02` | Centrifugal pump | temperature, vibration |
| `pump-03` | Booster pump | temperature, vibration, pressure |
| `valve-01` | Control valve | pressure, flow |
| `valve-02` | Control valve | pressure, flow |
| `compressor-01` | Compressor | temperature, pressure, vibration |
| `flowmeter-01` | Inline flow meter | flow |

**Zone 2 — Processing & Compression** (7 devices)

| Device ID | Type | Reports |
|---|---|---|
| `compressor-02` | Compressor | temperature, pressure, vibration |
| `compressor-03` | Compressor | temperature, pressure, vibration |
| `heat-exchanger-01` | Heat exchanger | temperature, pressure |
| `separator-01` | Gas/liquid separator | pressure, flow |
| `valve-03` | Control valve | pressure, flow |
| `valve-04` | Control valve | pressure, flow |
| `pump-04` | Process pump | temperature, vibration |

**Zone 3 — Storage & Distribution** (6 devices)

| Device ID | Type | Reports |
|---|---|---|
| `tank-01` | Storage tank | temperature, pressure |
| `tank-02` | Storage tank | temperature, pressure |
| `export-pump-01` | Export pump | temperature, vibration, pressure |
| `export-pump-02` | Export pump | temperature, vibration, pressure |
| `valve-05` | Export valve | pressure, flow |
| `flowmeter-02` | Export flow meter | flow |

20 devices total (7 + 7 + 6), matching the simulator scope.

## 2026-08-22 — Normal ranges per reading type

| Reading type | Normal range | Unit |
|---|---|---|
| temperature | 40–90 | °C |
| pressure | 1–10 | bar |
| vibration | 0–15 | mm/s |
| flow | 0–500 | m³/h |

Values drift around the previous reading (small random step) rather than
being redrawn independently each time — that reads like a real sensor
instead of noise.

## 2026-08-22 — Bad data is injected on purpose

~1–2% of readings are deliberately malformed or out-of-range (missing
field, value far outside the normal band). Without this, the schema
validation, dbt tests, and Great Expectations checkpoint never have
anything real to catch — the quality layer would be unproven.
