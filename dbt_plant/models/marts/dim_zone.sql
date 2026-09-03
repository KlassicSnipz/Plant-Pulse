with distinct_zones as (
    select distinct zone as zone_name
    from {{ ref('stg_raw_readings') }}
)

select
    row_number() over (order by zone_name) as zone_key,
    zone_name
from distinct_zones
