select
    plant_id,
    plant_name,
    region,
    plant_type,
    cast(capacity_units_per_day as integer) as capacity_units_per_day
from {{ ref('dim_plant') }}
