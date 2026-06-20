-- OEE = Availability x Performance x Quality
--
-- Unit-economics assumptions (documented here, not buried in a notebook):
--   IDEAL_RATE_UNITS_PER_SHIFT = 350   -- theoretical max units in an 8-hr shift at this line type
--   UNIT_MARGIN_USD            = 40    -- contribution margin per unit, used for "lost revenue" calc
--   SCRAP_COST_PER_UNIT_USD    = 22    -- material + labor sunk into a scrapped unit
--
-- These are illustrative constants for a portfolio project. In a real engagement these would
-- come from Finance/Standard Costing, not be hardcoded — call this out explicitly in interviews.

{% set ideal_rate_units_per_shift = 350 %}
{% set unit_margin_usd = 40 %}
{% set scrap_cost_per_unit_usd = 22 %}

with run_level as (
    select
        run_date,
        line_id,
        plant_id,
        sum(planned_runtime_min) as planned_runtime_min,
        sum(actual_runtime_min) as actual_runtime_min,
        sum(downtime_minutes) as downtime_minutes,
        sum(units_produced) as units_produced,
        sum(units_defective) as units_defective,
        sum(downtime_cost_usd) as downtime_cost_usd,
        count(*) as shift_count
    from {{ ref('fct_production_run_enriched') }}
    group by run_date, line_id, plant_id
)

select
    run_date,
    line_id,
    plant_id,
    planned_runtime_min,
    downtime_minutes,
    units_produced,
    units_defective,

    -- Availability: actual run time vs planned run time
    round(actual_runtime_min * 1.0 / planned_runtime_min, 4) as availability,

    -- Performance: actual output vs theoretical max output for the time scheduled
    round(
        least(1.0, units_produced * 1.0 / ({{ ideal_rate_units_per_shift }} * shift_count)),
        4
    ) as performance,

    -- Quality: good units vs total units
    round((units_produced - units_defective) * 1.0 / units_produced, 4) as quality,

    -- OEE = Availability x Performance x Quality
    round(
        (actual_runtime_min * 1.0 / planned_runtime_min)
        * least(1.0, units_produced * 1.0 / ({{ ideal_rate_units_per_shift }} * shift_count))
        * ((units_produced - units_defective) * 1.0 / units_produced),
        4
    ) as oee,

    -- Financial Impact KPIs
    downtime_cost_usd,
    round(units_defective * {{ scrap_cost_per_unit_usd }}, 2) as scrap_cost_usd,
    round(
        (downtime_minutes / 480.0) * {{ ideal_rate_units_per_shift }} * {{ unit_margin_usd }},
        2
    ) as lost_production_revenue_usd

from run_level
