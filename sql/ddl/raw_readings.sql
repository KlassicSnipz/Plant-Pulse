CREATE TABLE raw_readings (
    id BIGSERIAL PRIMARY KEY,
    device_id TEXT,
    zone TEXT,
    reading_type TEXT,
    value NUMERIC,
    unit TEXT,
    reading_ts TIMESTAMPTZ,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    quality_flag TEXT NOT NULL DEFAULT 'ok'
);