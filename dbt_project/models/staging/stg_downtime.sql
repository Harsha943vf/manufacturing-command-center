with machine_downtime as (
    select
        downtime_id,
        run_id,
        machine_id,
        cast(date as date) as downtime_date,
        reason_code,
        cast(duration_minutes as integer) as duration_minutes,
        cast(cost_impact_usd as double) as cost_impact_usd,
        cast(null as varchar) as supplier_id,
        cast(null as varchar) as material_id,
        cast(null as varchar) as line_id
    from {{ ref('fact_downtime') }}
),

material_shortage_downtime as (
    select
        downtime_id,
        run_id,
        machine_id,
        cast(date as date) as downtime_date,
        reason_code,
        cast(duration_minutes as integer) as duration_minutes,
        cast(cost_impact_usd as double) as cost_impact_usd,
        supplier_id,
        material_id,
        line_id
    from {{ ref('fact_material_shortage_downtime') }}
)

select * from machine_downtime
union all
select * from material_shortage_downtime
