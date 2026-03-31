-- stg_order_items.sql
-- Line items with product details from SOURCE_DATA.RAW_ORDER_ITEMS

with items as (
    select * from {{ source('source_data', 'raw_order_items') }}
),

products as (
    select * from {{ source('source_data', 'raw_products') }}
),

staged as (
    select
        i.order_item_id::int                    as order_item_id,
        i.order_id::int                         as order_id,
        i.product_id::int                       as product_id,
        p.product_name,
        p.category                              as product_category,
        i.quantity::int                          as quantity,
        p.unit_price::decimal(10,2)             as unit_price,
        i.line_total::decimal(12,2)             as line_total
    from items i
    left join products p on i.product_id = p.product_id
)

select * from staged
