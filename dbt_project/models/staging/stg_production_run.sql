select
    run_id,
    cast(date as date) as run_date,
    shift,
    line_id,
    machine_id,
    work_order_id,
    cast(planned_runtime_min as integer) as planned_runtime_min,
    cast(units_produced as integer) as units_produced,
    cast(units_defective as integer) as units_defective,
    cast(defect_rate as double) as defect_rate
from {{ ref('fact_production_run') }}
