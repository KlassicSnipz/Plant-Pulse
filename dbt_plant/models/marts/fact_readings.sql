with readings as (
    select * from {{ ref('stg_raw_readings') }}
),

devices as (
    select * from {{ ref('dim_device') }}
),

zones as (
    select * from {{ ref('dim_zone') }}
),

reading_types as (
    select * from {{ ref('dim_reading') }}
),

quality as (
    select * from {{ ref('dim_quality') }}
)

select
    readings.raw_reading_id as id,
    devices.device_key,
    zones.zone_key,
    reading_types.reading_key,
    quality.quality_key,
    readings.value,
    readings.reading_ts,
    readings.ingested_at
from readings
left join devices        on readings.device_id     = devices.device_id
left join zones          on readings.zone          = zones.zone_name
left join reading_types  on readings.reading_type  = reading_types.reading_type
left join quality        on readings.quality_flag  = quality.quality_flag
