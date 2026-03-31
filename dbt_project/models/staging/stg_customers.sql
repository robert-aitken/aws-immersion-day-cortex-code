-- stg_customers.sql
-- Cleaned customer records from SOURCE_DATA.RAW_CUSTOMERS

with source as (
    select * from {{ source('source_data', 'raw_customers') }}
),

staged as (
    select
        customer_id::int                        as customer_id,
        trim(first_name)                        as first_name,
        trim(last_name)                         as last_name,
        lower(trim(email))                      as email,
        upper(trim(region))                     as region,
        signup_date::date                       as signup_date
    from source
)

select * from staged
