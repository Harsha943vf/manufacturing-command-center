-- One row per production run, with downtime minutes joined in.
-- This is the grain that feeds the OEE calculation in fct_oee_daily.

with downtime_by_run as (
    select
        run_id,
        sum(duration_minutes) as downtime_minutes,
        sum(cost_impact_usd) as downtime_cost_usd
    from {{ ref('stg_downtime') }}
    where run_id is not null  -- excludes material-shortage rows, which aren't tied to a single run
    group by run_id
)

select
    pr.run_id,
    pr.run_date,
    pr.shift,
    pr.line_id,
    l.plant_id,
    pr.machine_id,
    pr.work_order_id,
    pr.planned_runtime_min,
    coalesce(dt.downtime_minutes, 0) as downtime_minutes,
    pr.planned_runtime_min - coalesce(dt.downtime_minutes, 0) as actual_runtime_min,
    pr.units_produced,
    pr.units_defective,
    pr.defect_rate,
    coalesce(dt.downtime_cost_usd, 0) as downtime_cost_usd
from {{ ref('stg_production_run') }} pr
left join {{ ref('stg_line') }} l on pr.line_id = l.line_id
left join downtime_by_run dt on pr.run_id = dt.run_id
