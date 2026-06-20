select
    supplier_id,
    supplier_name,
    region,
    cast(lpi_score as double) as lpi_score,
    tier,
    cast(on_time_delivery_rate as double) as on_time_delivery_rate
from {{ ref('dim_supplier') }}
