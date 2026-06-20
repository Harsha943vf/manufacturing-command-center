select
    work_order_id,
    product_id,
    customer_order_id,
    cast(planned_qty as integer) as planned_qty,
    priority,
    cast(due_date as date) as due_date
from {{ ref('dim_work_order') }}
