-- Operations Command Center: Top Risks Ranked by Financial Impact
--
-- This is the "what should I do next" layer. It unions two risk streams --
-- machine risk and supplier risk -- onto a common shape (risk_type, description,
-- financial_impact_usd, recommended_action) so they can be ranked together on one page.

with machine_risks as (
    select
        'Machine Risk' as risk_type,
        m.machine_id as entity_id,
        m.machine_type || ' ' || m.machine_id || ' (Line ' || m.line_id || ')' as description,
        m.machine_risk_score as risk_score,
        m.total_downtime_minutes * 65 as estimated_financial_impact_usd,  -- blended $/min across reason codes
        case
            when m.machine_risk_score >= 80 then 'Schedule maintenance within 48 hours'
            when m.machine_risk_score >= 50 then 'Add to next scheduled maintenance window'
            else 'Monitor -- no action needed'
        end as recommended_action
    from {{ ref('dim_machine_risk_score') }} m
),

supplier_risks as (
    select
        'Supplier Risk' as risk_type,
        s.supplier_id as entity_id,
        s.supplier_name || ' (' || s.region || ')' as description,
        s.supplier_risk_score as risk_score,
        s.total_shortage_cost_usd as estimated_financial_impact_usd,
        case
            when s.supplier_risk_score >= 70 then 'Identify alternate vendor for critical materials'
            when s.supplier_risk_score >= 40 then 'Renegotiate lead-time SLA / add buffer stock'
            else 'Monitor -- no action needed'
        end as recommended_action
    from {{ ref('dim_supplier_risk_score') }} s
),

combined as (
    select * from machine_risks
    union all
    select * from supplier_risks
)

select
    risk_type,
    entity_id,
    description,
    round(risk_score, 1) as risk_score,
    round(estimated_financial_impact_usd, 0) as estimated_financial_impact_usd,
    recommended_action,
    rank() over (order by estimated_financial_impact_usd desc) as impact_rank
from combined
where risk_score > 0 or estimated_financial_impact_usd > 0
order by estimated_financial_impact_usd desc
limit 10
