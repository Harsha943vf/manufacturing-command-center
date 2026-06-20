-- Supplier Risk Index (0-100)
--
-- NOTE ON FORMULA ADAPTATION:
-- The original spec weighted "Quality Performance" as a standalone factor, but this dataset
-- doesn't trace individual defects back to a specific incoming material/supplier (defects are
-- tracked at the production-run level, not the material-batch level -- a deliberate scope
-- decision to keep the generator realistic rather than fabricating a traceability chain that
-- doesn't typically exist in practice without a much larger MES integration). Instead, this
-- version uses "Demonstrated Downstream Impact" -- the actual dollar cost of material-shortage
-- downtime this supplier has caused -- which is arguably a more business-relevant signal anyway.
--
-- Final formula:
--   0.35 x Delivery Unreliability (observed late-delivery rate)
-- + 0.25 x Lead-Time Variability (stddev of delay days)
-- + 0.20 x Production Dependency (count + criticality of materials sourced from this supplier)
-- + 0.20 x Demonstrated Downstream Impact (dollar cost of shortage-driven downtime caused)

with delivery_stats as (
    select
        supplier_id,
        count(*) as total_deliveries,
        avg(1 - is_on_time) as late_rate,
        stddev(delay_days) as delay_days_stddev
    from {{ ref('stg_supplier_delivery') }}
    group by supplier_id
),

dependency_stats as (
    select
        supplier_id,
        count(*) as materials_sourced,
        sum(case when criticality_rank = 'Critical' then 1 else 0 end) as critical_materials_sourced
    from {{ ref('stg_material') }}
    group by supplier_id
),

impact_stats as (
    select
        supplier_id,
        sum(cost_impact_usd) as total_shortage_cost_usd
    from {{ ref('stg_downtime') }}
    where supplier_id is not null
    group by supplier_id
),

combined as (
    select
        s.supplier_id,
        s.supplier_name,
        s.region,
        s.lpi_score,
        s.tier,
        coalesce(ds.late_rate, 0) as late_rate,
        coalesce(ds.delay_days_stddev, 0) as delay_days_stddev,
        coalesce(dep.critical_materials_sourced, 0) as critical_materials_sourced,
        coalesce(imp.total_shortage_cost_usd, 0) as total_shortage_cost_usd
    from {{ ref('stg_supplier') }} s
    left join delivery_stats ds on s.supplier_id = ds.supplier_id
    left join dependency_stats dep on s.supplier_id = dep.supplier_id
    left join impact_stats imp on s.supplier_id = imp.supplier_id
),

normalized as (
    select
        *,
        (late_rate - min(late_rate) over ()) /
            nullif(max(late_rate) over () - min(late_rate) over (), 0) as late_rate_norm,

        (delay_days_stddev - min(delay_days_stddev) over ()) /
            nullif(max(delay_days_stddev) over () - min(delay_days_stddev) over (), 0) as variability_norm,

        (critical_materials_sourced - min(critical_materials_sourced) over ()) /
            nullif(max(critical_materials_sourced) over () - min(critical_materials_sourced) over (), 0) as dependency_norm,

        (total_shortage_cost_usd - min(total_shortage_cost_usd) over ()) /
            nullif(max(total_shortage_cost_usd) over () - min(total_shortage_cost_usd) over (), 0) as impact_norm
    from combined
)

select
    supplier_id,
    supplier_name,
    region,
    lpi_score,
    tier,
    round(late_rate, 3) as observed_late_rate,
    critical_materials_sourced,
    round(total_shortage_cost_usd, 2) as total_shortage_cost_usd,
    round(
        100 * (
            0.35 * coalesce(late_rate_norm, 0) +
            0.25 * coalesce(variability_norm, 0) +
            0.20 * coalesce(dependency_norm, 0) +
            0.20 * coalesce(impact_norm, 0)
        ), 1
    ) as supplier_risk_score
from normalized
order by supplier_risk_score desc
