with source as (
    select * from {{ source('raw', 'raw_readings') }}
),

cleaned as (
    select
        id as raw_reading_id,
        device_id,
        zone,
        reading_type,
        value::numeric as value,
        unit,
        reading_ts::timestamptz as reading_ts,
        ingested_at::timestamptz as ingested_at,
        quality_flag
    from source
)

select * from cleaned
