"""Device inventory and reading-type specifications for the simulated plant.

Single source of truth for what exists in the plant. Mirrors the inventory
documented in docs/DECISIONS.md — if you change one, change the other.

Devices only report reading types that make physical sense for them: things
with moving parts (pumps, compressors) report vibration, things without
(valves, tanks, flow meters) do not.
"""

# Normal operating band per reading type.
#   unit        : what the value is measured in
#   low / high  : the normal operating range
#   step        : typical size of one drift increment (as a fraction of the band)
READING_TYPES = {
    "temperature": {"unit": "C",    "low": 40.0, "high": 90.0,  "step": 0.02},
    "pressure":    {"unit": "bar",  "low": 1.0,  "high": 10.0,  "step": 0.03},
    "vibration":   {"unit": "mm/s", "low": 0.0,  "high": 15.0,  "step": 0.05},
    "flow":        {"unit": "m3/h", "low": 0.0,  "high": 500.0, "step": 0.02},
}

# The plant: 20 devices across 3 zones, following the process flow
# intake -> processing -> storage/export.
DEVICES = [
    # --- Zone 1: Intake & Pumping (7 devices) ---
    {"device_id": "pump-01",           "device_type": "centrifugal_pump", "zone": "zone-1",
     "reading_types": ["temperature", "vibration"]},
    {"device_id": "pump-02",           "device_type": "centrifugal_pump", "zone": "zone-1",
     "reading_types": ["temperature", "vibration"]},
    {"device_id": "pump-03",           "device_type": "booster_pump",     "zone": "zone-1",
     "reading_types": ["temperature", "vibration", "pressure"]},
    {"device_id": "valve-01",          "device_type": "control_valve",    "zone": "zone-1",
     "reading_types": ["pressure", "flow"]},
    {"device_id": "valve-02",          "device_type": "control_valve",    "zone": "zone-1",
     "reading_types": ["pressure", "flow"]},
    {"device_id": "compressor-01",     "device_type": "compressor",       "zone": "zone-1",
     "reading_types": ["temperature", "pressure", "vibration"]},
    {"device_id": "flowmeter-01",      "device_type": "flow_meter",       "zone": "zone-1",
     "reading_types": ["flow"]},

    # --- Zone 2: Processing & Compression (7 devices) ---
    {"device_id": "compressor-02",     "device_type": "compressor",       "zone": "zone-2",
     "reading_types": ["temperature", "pressure", "vibration"]},
    {"device_id": "compressor-03",     "device_type": "compressor",       "zone": "zone-2",
     "reading_types": ["temperature", "pressure", "vibration"]},
    {"device_id": "heat-exchanger-01", "device_type": "heat_exchanger",   "zone": "zone-2",
     "reading_types": ["temperature", "pressure"]},
    {"device_id": "separator-01",      "device_type": "separator",        "zone": "zone-2",
     "reading_types": ["pressure", "flow"]},
    {"device_id": "valve-03",          "device_type": "control_valve",    "zone": "zone-2",
     "reading_types": ["pressure", "flow"]},
    {"device_id": "valve-04",          "device_type": "control_valve",    "zone": "zone-2",
     "reading_types": ["pressure", "flow"]},
    {"device_id": "pump-04",           "device_type": "process_pump",     "zone": "zone-2",
     "reading_types": ["temperature", "vibration"]},

    # --- Zone 3: Storage & Distribution (6 devices) ---
    {"device_id": "tank-01",           "device_type": "storage_tank",     "zone": "zone-3",
     "reading_types": ["temperature", "pressure"]},
    {"device_id": "tank-02",           "device_type": "storage_tank",     "zone": "zone-3",
     "reading_types": ["temperature", "pressure"]},
    {"device_id": "export-pump-01",    "device_type": "export_pump",      "zone": "zone-3",
     "reading_types": ["temperature", "vibration", "pressure"]},
    {"device_id": "export-pump-02",    "device_type": "export_pump",      "zone": "zone-3",
     "reading_types": ["temperature", "vibration", "pressure"]},
    {"device_id": "valve-05",          "device_type": "export_valve",     "zone": "zone-3",
     "reading_types": ["pressure", "flow"]},
    {"device_id": "flowmeter-02",      "device_type": "flow_meter",       "zone": "zone-3",
     "reading_types": ["flow"]},
]


def streams():
    """Yield every (device, reading_type) pair the plant produces.

    A 'stream' is one device reporting one kind of measurement — that is the
    real unit of data in this pipeline, not the device itself.
    """
    for device in DEVICES:
        for reading_type in device["reading_types"]:
            yield device, reading_type
