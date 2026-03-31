-- assert_order_total_positive.sql
-- Custom test: all order totals should be positive (catches data quality issues)

select
    order_id,
    order_total
from {{ ref('fct_orders') }}
where order_total <= 0
