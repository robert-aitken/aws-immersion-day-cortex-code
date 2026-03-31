-- stg_orders.sql
-- Cleaned and type-cast order headers from SOURCE_DATA.RAW_ORDERS

with source as (
    select * from {{ source('source_data', 'raw_orders') }}
),

staged as (
    select
        order_id::int                           as order_id,
        customer_id::int                        as customer_id,
        order_date::date                        as order_date,
        upper(trim(status))                     as order_status,
        total_amount::decimal(12,2)             as total_amount,
        created_at::timestamp_ntz               as created_at
    from source
)

select * from staged
