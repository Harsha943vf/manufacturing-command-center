{% snapshot supplier_reliability_snapshot %}

{{
    config(
        target_schema='snapshots',
        unique_key='supplier_id',
        strategy='check',
        check_cols=['on_time_delivery_rate', 'tier', 'lpi_score'],
    )
}}

select
    supplier_id,
    supplier_name,
    region,
    lpi_score,
    tier,
    on_time_delivery_rate
from {{ ref('stg_supplier') }}

{% endsnapshot %}
