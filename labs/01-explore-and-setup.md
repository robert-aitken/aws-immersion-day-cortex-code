# Lab 01: Explore and Setup

**Duration**: 20-30 minutes

## Objective

Use CoCo CLI to run the Snowflake setup, load the seed data, explore the workshop
repository, and understand the core dbt pipeline before you debug it.

> **Prerequisite**: You should have completed Lab 00 and confirmed the EC2 jumphost,
> CLI tools, and Snowflake connection are ready.

## Step 1: Launch CoCo CLI

From your EC2 jumphost:

```bash
cd ~/workshop
cortex -c DEMO
```

CoCo will automatically read the `AGENTS.md` file and understand the workshop context.

## Step 2: Create the Snowflake Workshop Objects

Ask CoCo to run the setup script:

```
Run the Snowflake setup script at scripts/snowflake-setup.sql using my DEMO connection.
Summarize what it creates.
```

You should end up with:

| Object | Name |
|---|---|
| Role | `COCO_WORKSHOP_ROLE` |
| Warehouse | `COCO_WORKSHOP_WH` |
| Database | `COCO_WORKSHOP` |
| Schemas | `SOURCE_DATA`, `STAGING`, `MARTS` |
| Source Tables | `RAW_CUSTOMERS`, `RAW_PRODUCTS`, `RAW_ORDERS`, `RAW_ORDER_ITEMS` |
| Stage | `seed_stage` (optional for local file loading) |

## Step 3: Load Seed Data from Public S3

For the core workshop path, load the Parquet seed files directly from the public workshop bucket in `us-west-2`. This avoids shell-script and local-file issues.

Ask CoCo:

```
Create a stage over s3://aws-immersion-day-cortex-code-public/data/seed/ and load the four Parquet files into COCO_WORKSHOP.SOURCE_DATA.
Then verify the row counts.
```

If you want to run it manually, use Snowflake SQL like this:

```sql
USE ROLE COCO_WORKSHOP_ROLE;
USE WAREHOUSE COCO_WORKSHOP_WH;
USE SCHEMA COCO_WORKSHOP.SOURCE_DATA;

CREATE OR REPLACE FILE FORMAT public_parquet_format TYPE = PARQUET;

CREATE OR REPLACE STAGE public_seed_stage
  URL = 's3://aws-immersion-day-cortex-code-public/data/seed/'
  FILE_FORMAT = public_parquet_format;

TRUNCATE TABLE RAW_CUSTOMERS;
COPY INTO RAW_CUSTOMERS
FROM (
  SELECT $1:customer_id::INT,
         $1:first_name::VARCHAR,
         $1:last_name::VARCHAR,
         $1:email::VARCHAR,
         $1:region::VARCHAR,
         $1:signup_date::VARCHAR
  FROM @public_seed_stage/raw_customers.parquet
);

TRUNCATE TABLE RAW_PRODUCTS;
COPY INTO RAW_PRODUCTS
FROM (
  SELECT $1:product_id::INT,
         $1:product_name::VARCHAR,
         $1:category::VARCHAR,
         $1:unit_price::DECIMAL(10,2)
  FROM @public_seed_stage/raw_products.parquet
);

TRUNCATE TABLE RAW_ORDERS;
COPY INTO RAW_ORDERS
FROM (
  SELECT $1:order_id::INT,
         $1:customer_id::INT,
         $1:order_date::VARCHAR,
         $1:status::VARCHAR,
         $1:total_amount::DECIMAL(12,2),
         $1:created_at::VARCHAR
  FROM @public_seed_stage/raw_orders.parquet
);

TRUNCATE TABLE RAW_ORDER_ITEMS;
COPY INTO RAW_ORDER_ITEMS
FROM (
  SELECT $1:order_item_id::INT,
         $1:order_id::INT,
         $1:product_id::INT,
         $1:quantity::INT,
         $1:line_total::DECIMAL(12,2)
  FROM @public_seed_stage/raw_order_items.parquet
);
```

Expected row counts:

| Table | Rows |
|---|---|
| `RAW_CUSTOMERS` | ~1,000 |
| `RAW_PRODUCTS` | ~200 |
| `RAW_ORDERS` | ~10,000 |
| `RAW_ORDER_ITEMS` | ~35,000 |

## Step 4: Explore the Repository

Ask CoCo to explain the project:

```
What's in this repository? Walk me through the architecture.
```

CoCo should describe:
- The dbt project with staging and mart models
- The setup SQL that creates the Snowflake objects for the workshop
- The optional MWAA orchestration files kept for the advanced capstone lab

## Step 5: Explore the Source Data

Ask CoCo to look at the data that you just loaded:

```
How many rows are in each source table? Show me a sample of 5 rows from raw_orders.
```

Expected counts:
| Table | Rows |
|---|---|
| RAW_ORDERS | ~10,000 |
| RAW_CUSTOMERS | ~1,000 |
| RAW_PRODUCTS | ~200 |
| RAW_ORDER_ITEMS | ~35,000 |

## Step 6: Understand the dbt Project

Ask CoCo:

```
Read the dbt project in dbt_project/ and explain the model dependencies.
Which models depend on which?
```

CoCo should show:
```
stg_orders      ← raw_orders
stg_customers   ← raw_customers
stg_order_items ← raw_order_items + raw_products
fct_orders      ← stg_orders + stg_order_items
dim_customers   ← stg_customers + fct_orders
```

## What You've Learned

- How to use CoCo CLI to run setup tasks and explore a repository
- How to load Parquet data into Snowflake from a public S3 stage
- The core workshop architecture: source data -> staging -> marts
- How dbt model dependencies work before you attempt the bug-fix lab
