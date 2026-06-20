select
    delivery_id,
    supplier_id,
    material_id,
    cast(scheduled_date as date) as scheduled_date,
    cast(actual_date as date) as actual_date,
    cast(delay_days as integer) as delay_days,
    cast(qty_ordered as integer) as qty_ordered,
    cast(qty_received as integer) as qty_received,
    case when delay_days = 0 then 1 else 0 end as is_on_time
from {{ ref('fact_supplier_delivery') }}
