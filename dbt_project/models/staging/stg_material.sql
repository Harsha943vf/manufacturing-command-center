select
    material_id,
    material_name,
    category,
    supplier_id,
    criticality_rank
from {{ ref('dim_material') }}
