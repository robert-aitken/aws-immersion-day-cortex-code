-- dim_customers.sql
-- Customer dimension with lifetime metrics.
-- Depends on fct_orders — will fail if fct_orders has errors.

with customers as (
    select * from {{ ref('stg_customers') }}
),

orders as (
    select * from {{ ref('fct_orders') }}
),

customer_metrics as (
    select
        customer_id,
        count(*)                                as lifetime_orders,
        sum(order_total)                        as lifetime_revenue,
        min(order_date)                         as first_order_date,
        max(order_date)                         as last_order_date,
        avg(order_total)                        as avg_order_value
    from orders
    group by customer_id
),

final as (
    select
        c.customer_id,
        c.first_name,
        c.last_name,
        c.email,
        c.region,
        c.signup_date,
        coalesce(m.lifetime_orders, 0)          as lifetime_orders,
        coalesce(m.lifetime_revenue, 0)         as lifetime_revenue,
        m.first_order_date,
        m.last_order_date,
        coalesce(m.avg_order_value, 0)          as avg_order_value,
        datediff('day', c.signup_date,
                 coalesce(m.first_order_date, current_date()))
                                                as days_to_first_order
    from customers c
    left join customer_metrics m on c.customer_id = m.customer_id
)

select * from final
