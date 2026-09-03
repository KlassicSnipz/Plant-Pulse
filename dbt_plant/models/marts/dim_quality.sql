with distinct_quality_flags as (
    select distinct quality_flag
    from {{ ref('stg_raw_readings') }}
)

select
    row_number() over (order by quality_flag) as quality_key,
    quality_flag
from distinct_quality_flags
