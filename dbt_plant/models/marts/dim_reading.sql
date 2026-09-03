with distinct_reading_types as (
    select distinct reading_type, unit
    from {{ ref('stg_raw_readings') }}
)

select
    row_number() over (order by reading_type) as reading_key,
    reading_type,
    unit
from distinct_reading_types
