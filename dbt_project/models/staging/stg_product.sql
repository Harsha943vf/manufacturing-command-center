select
    product_id,
    sku,
    product_family,
    margin_class
from {{ ref('dim_product') }}
