# AWS Immersion Day: AI-Accelerated Data Engineering

You are helping a workshop participant build and debug an e-commerce data pipeline
on Snowflake, orchestrated by Amazon MWAA (Airflow), with a QuickSight dashboard
as the final output.

## Repository Layout

- `cfn/workshop-template.yaml` — CloudFormation template that provisions EC2, MWAA, S3, IAM, QuickSight
- `dags/ecommerce_pipeline.py` — Airflow DAG with tasks: load seed data, dbt run, dbt test, QuickSight refresh
- `dbt_project/` — dbt project with staging + mart models (NOTE: there is a deliberate bug in `models/marts/fct_orders.sql`)
- `data/seed/` — Parquet files with e-commerce sample data (~10K orders, 1K customers, 200 products, 35K line items)
- `labs/` — Step-by-step lab instructions (00 through 04)
- `scripts/bootstrap-ec2.sh` — EC2 UserData bootstrap script

## Snowflake Environment

- **Database**: `COCO_WORKSHOP`
- **Schemas**: `SOURCE_DATA` (raw tables), `STAGING` (stg_ models), `MARTS` (fct/dim models)
- **Warehouse**: `COCO_WORKSHOP_WH` (X-Small, auto-suspend 120s)
- **Role**: `COCO_WORKSHOP_ROLE`
- **Connection**: configured in `~/.snowflake/config.toml` as connection `DEMO`

## Source Tables (in COCO_WORKSHOP.SOURCE_DATA)

| Table | Key Columns | Rows |
|---|---|---|
| `RAW_ORDERS` | order_id, customer_id, order_date, status, total_amount | ~10,000 |
| `RAW_CUSTOMERS` | customer_id, first_name, last_name, email, region, signup_date | ~1,000 |
| `RAW_PRODUCTS` | product_id, product_name, category, unit_price | ~200 |
| `RAW_ORDER_ITEMS` | order_item_id, order_id, product_id, quantity, line_total | ~35,000 |

## dbt Project Structure

### Staging Models (COCO_WORKSHOP.STAGING)
- `stg_orders` — Cleaned orders with type casting and column standardisation
- `stg_customers` — Cleaned customer records with region normalisation
- `stg_order_items` — Line items joined with products to get unit_price

### Mart Models (COCO_WORKSHOP.MARTS)
- `fct_orders` — Order fact table with aggregated line items. **Contains a deliberate bug**: references column `TOTAL_AMOUNT` instead of the correct `ORDER_TOTAL` in the final SELECT
- `dim_customers` — Customer dimension with lifetime value (depends on fct_orders)

## The Planted Bug

In `dbt_project/models/marts/fct_orders.sql`, the final SELECT references `order_totals.TOTAL_AMOUNT` but the CTE column is actually named `ORDER_TOTAL`. This causes:
1. A dbt compilation/run error on the fct_orders model
2. A cascade failure on dim_customers (which depends on fct_orders)
3. The MWAA DAG fails at the `dbt_run` task

The fix is to change `TOTAL_AMOUNT` to `ORDER_TOTAL` in fct_orders.sql.

## MWAA Pipeline

The Airflow DAG `ecommerce_pipeline` runs these tasks in sequence:
1. `load_seed_data` — Copies Parquet files from S3 to Snowflake source tables
2. `dbt_run` — Executes `dbt run` against the dbt project
3. `dbt_test` — Runs `dbt test` to validate data quality
4. `refresh_quicksight` — Triggers a SPICE dataset refresh in Amazon QuickSight

## Workshop Flow

Participants should work through the labs in order:
1. **Lab 00**: Verify environment (EC2, CoCo, Snowflake connectivity)
2. **Lab 01**: Explore source data and understand the pipeline architecture
3. **Lab 02**: Trigger the pipeline, observe the failure, use CoCo to debug and fix
4. **Lab 03**: Re-run the pipeline successfully, verify mart tables
5. **Lab 04**: Confirm QuickSight SPICE refresh and build a simple dashboard

## Key CoCo Skills Used

- `analyzing-data` — Querying and exploring Snowflake tables
- `dbt-projects-on-snowflake` — Working with dbt projects deployed to Snowflake
- `lineage` — Tracing data dependencies to understand the bug's impact
- `dynamic-tables` — Optional: creating Dynamic Tables for real-time aggregation
- `dashboard` — Optional: building Snowflake-native dashboards
