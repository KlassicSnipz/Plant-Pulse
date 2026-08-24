READING_TYPES = {
    "temperature": {"unit": "C",    "low": 40.0, "high": 90.0,  "step": 0.02},
    "pressure":    {"unit": "bar",  "low": 1.0,  "high": 10.0,  "step": 0.03},
    "vibration":   {"unit": "mm/s", "low": 0.0,  "high": 15.0,  "step": 0.05},
    "flow":        {"unit": "m3/h", "low": 0.0,  "high": 500.0, "step": 0.02},
}

DEVICES = [
    {"device_id": "pump-01", "zone": "zone-1", "reading_types": ["temperature", "vibration"]},
    {"device_id": "pump-02", "zone": "zone-1", "reading_types": ["temperature", "vibration"]},
    {"device_id": "pump-03", "zone": "zone-1", "reading_types": ["temperature", "vibration", "pressure"]},
    {"device_id": "valve-01", "zone": "zone-1", "reading_types": ["pressure", "flow"]},
    {"device_id": "valve-02", "zone": "zone-1", "reading_types": ["pressure", "flow"]},
    {"device_id": "compressor-01", "zone": "zone-1", "reading_types": ["temperature", "pressure", "vibration"]},
    {"device_id": "flowmeter-01", "zone": "zone-1", "reading_types": ["flow"]},

    {"device_id": "compressor-02", "zone": "zone-2", "reading_types": ["temperature", "pressure", "vibration"]},
    {"device_id": "compressor-03", "zone": "zone-2", "reading_types": ["temperature", "pressure", "vibration"]},
    {"device_id": "heat-exchanger-01", "zone": "zone-2", "reading_types": ["temperature", "pressure"]},
    {"device_id": "separator-01", "zone": "zone-2", "reading_types": ["pressure", "flow"]},
    {"device_id": "valve-03", "zone": "zone-2", "reading_types": ["pressure", "flow"]},
    {"device_id": "valve-04", "zone": "zone-2", "reading_types": ["pressure", "flow"]},
    {"device_id": "pump-04", "zone": "zone-2", "reading_types": ["temperature", "vibration"]},

    {"device_id": "tank-01", "zone": "zone-3", "reading_types": ["temperature", "pressure"]},
    {"device_id": "tank-02", "zone": "zone-3", "reading_types": ["temperature", "pressure"]},
    {"device_id": "export-pump-01", "zone": "zone-3", "reading_types": ["temperature", "vibration", "pressure"]},
    {"device_id": "export-pump-02", "zone": "zone-3", "reading_types": ["temperature", "vibration", "pressure"]},
    {"device_id": "valve-05", "zone": "zone-3", "reading_types": ["pressure", "flow"]},
    {"device_id": "flowmeter-02", "zone": "zone-3", "reading_types": ["flow"]},
]
