-- Machine Maintenance Risk Score (0-100)
--
-- Weighted combination of:
--   - MTBF (inverse: lower MTBF = higher risk)          weight 0.30
--   - Downtime frequency (failures per run)               weight 0.30
--   - Cycle-time deviation (CV of units_produced)         weight 0.20
--   - Repair history (total downtime minutes)             weight 0.20
--
-- Each component is min-max normalized across all machines (0-1), then weighted and scaled to 0-100.
-- This is deliberately transparent and explainable -- a plant manager can see exactly why a
-- machine scored 92 vs 18, which a black-box anomaly-detection model would not offer.

with machine_stats as (
    select
        m.machine_id,
        m.line_id,
        m.machine_type,
        count(pr.run_id) as total_runs,
        sum(pr.planned_runtime_min) as total_planned_minutes,
        avg(pr.units_produced) as avg_units_produced,
        stddev(pr.units_produced) as stddev_units_produced,
        count(d.downtime_id) as total_failures,
        sum(coalesce(d.duration_minutes, 0)) as total_downtime_minutes
    from {{ ref('stg_machine') }} m
    left join {{ ref('stg_production_run') }} pr on m.machine_id = pr.machine_id
    left join {{ ref('stg_downtime') }} d on pr.run_id = d.run_id
    group by m.machine_id, m.line_id, m.machine_type
),

derived as (
    select
        *,
        -- MTBF: total operating minutes / number of failures (higher = healthier)
        case when total_failures = 0 then total_planned_minutes
             else total_planned_minutes * 1.0 / total_failures end as mtbf_minutes,
        -- Downtime frequency: failures per run
        total_failures * 1.0 / nullif(total_runs, 0) as downtime_frequency,
        -- Cycle-time deviation proxy: coefficient of variation of output
        coalesce(stddev_units_produced, 0) / nullif(avg_units_produced, 0) as cycle_time_cv
    from machine_stats
),

normalized as (
    select
        *,
        -- Invert and normalize MTBF: lower MTBF -> higher risk contribution
        1.0 - (mtbf_minutes - min(mtbf_minutes) over ()) /
              nullif(max(mtbf_minutes) over () - min(mtbf_minutes) over (), 0) as mtbf_risk_norm,

        (downtime_frequency - min(downtime_frequency) over ()) /
              nullif(max(downtime_frequency) over () - min(downtime_frequency) over (), 0) as downtime_freq_norm,

        (cycle_time_cv - min(cycle_time_cv) over ()) /
              nullif(max(cycle_time_cv) over () - min(cycle_time_cv) over (), 0) as cycle_time_norm,

        (total_downtime_minutes - min(total_downtime_minutes) over ()) /
              nullif(max(total_downtime_minutes) over () - min(total_downtime_minutes) over (), 0) as repair_history_norm
    from derived
)

select
    machine_id,
    line_id,
    machine_type,
    total_runs,
    total_failures,
    round(mtbf_minutes, 1) as mtbf_minutes,
    round(total_downtime_minutes, 1) as total_downtime_minutes,
    round(
        100 * (
            0.30 * coalesce(mtbf_risk_norm, 0) +
            0.30 * coalesce(downtime_freq_norm, 0) +
            0.20 * coalesce(cycle_time_norm, 0) +
            0.20 * coalesce(repair_history_norm, 0)
        ), 1
    ) as machine_risk_score

from normalized
order by machine_risk_score desc
