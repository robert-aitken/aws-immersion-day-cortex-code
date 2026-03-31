-- fct_orders.sql
-- Order fact table: joins order headers with aggregated line items.
--
-- ⚠️  THIS MODEL CONTAINS A DELIBERATE BUG FOR THE WORKSHOP.
--     The final SELECT references `order_totals.TOTAL_AMOUNT` but the CTE
--     column is actually named `ORDER_TOTAL`. Participants must find and fix this.

with orders as (
    select * from {{ ref('stg_orders') }}
),

order_items as (
    select * from {{ ref('stg_order_items') }}
),

-- Aggregate line items per order
order_totals as (
    select
        order_id,
        count(*)                                as item_count,
        sum(quantity)                           as total_units,
        sum(line_total)                         as order_total   -- ← This is the correct column name
    from order_items
    group by order_id
),

final as (
    select
        o.order_id,
        o.customer_id,
        o.order_date,
        o.order_status,
        ot.item_count,
        ot.total_units,
        ot.TOTAL_AMOUNT                         as order_total,  -- ← BUG: should be ot.ORDER_TOTAL
        o.total_amount                          as header_total,
        o.created_at
    from orders o
    left join order_totals ot on o.order_id = ot.order_id
)

select * from final
