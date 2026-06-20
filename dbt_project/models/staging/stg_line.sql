select
    line_id,
    plant_id,
    line_name
from {{ ref('dim_line') }}
