with distinct_devices as (
    select distinct device_id
    from {{ ref('stg_raw_readings') }}
)

select
    row_number() over (order by device_id) as device_key,
    device_id
from distinct_devices
