# AWS Immersion Day: AI-Accelerated Data Engineering

You are helping a workshop participant through a core workshop path focused on
Snowflake setup, seed-data loading, repository exploration, debugging a dbt
project, and building a Streamlit data product on top of the clean marts layer.

Amazon MWAA and Iceberg/Glue content exist in this repo as advanced or
instructor-led extensions and should not be treated as guaranteed participant
outcomes. QuickSight has been removed from the participant journey.

## Repository Layout

- `cfn/workshop-template.yaml` — CloudFormation template for the EC2 core path plus optional AWS extension resources
- `dags/ecommerce_pipeline.py` — Optional Airflow DAG for advanced MWAA orchestration labs
- `dbt_project/` — dbt project with staging + mart models (NOTE: there is a deliberate bug in `models/marts/fct_orders.sql`)
- `data/seed/` — Parquet files with e-commerce sample data (~10K orders, 1K customers, 200 products, 35K line items)
- `labs/` — Step-by-step lab instructions (00 through 05)
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
3. Anything downstream of the marts (a Streamlit app, a semantic view, an optional MWAA DAG run) breaks for the same reason

The fix is to change `TOTAL_AMOUNT` to `ORDER_TOTAL` in fct_orders.sql.

## Lab 03: From Pipeline to Product (Core App Challenge)

After the dbt fix, Lab 03 is a creative build challenge, not a walkthrough. Participants use CoCo to build a Streamlit app on top of `COCO_WORKSHOP.MARTS`. It is scored on clarity, usefulness, creativity, interaction, and finish.

Tiers:
- **Bronze**: 2+ charts, at least one filter, one "insight" section over the marts layer
- **Silver**: polished version of Bronze with drilldowns, comparisons, narrative copy, consistent styling
- **Gold**: add a Snowflake semantic view over the marts and a Cortex Analyst chat panel inside the app
- **Platinum**: add Snowflake-native ML — forecasting, anomaly detection, or "attention needed" scoring. Do **not** frame this as a classic product recommender; the current dataset does not have the interaction data to make that compelling. Forecasting weekly/monthly revenue by region or category, or detecting anomalies in daily order volume or AOV, are much stronger fits.

When guiding users in Lab 03:
- Encourage them to pick a persona (exec, sales hunter, analyst, ops) before writing any code
- Push for small prompt iterations rather than one giant prompt
- Offer the Snowflake connection name `DEMO` for any Python/Streamlit scaffolding
- Prefer `snowflake.connector` with `connection_name="DEMO"` or Streamlit in Snowflake

## Optional Lab 04: MWAA Pipeline

The Airflow DAG `ecommerce_pipeline` runs these tasks in sequence when the advanced environment is fully prepared:
1. `load_seed_data` — Copies Parquet files from S3 to Snowflake source tables
2. `dbt_run` — Executes `dbt run` against the dbt project
3. `dbt_test` — Runs `dbt test` to validate data quality

The DAG source may still contain a legacy `refresh_quicksight` task. It is not part of the supported workshop path. Treat it as deprecated — recommend removing or ignoring it when guiding participants.

## Workshop Flow

Participants should work through the labs in order:
1. **Lab 00**: Verify environment readiness on the EC2 jumphost
2. **Lab 01**: Run Snowflake setup, load seed data, and explore the project
3. **Lab 02**: Trigger the dbt failure, investigate it, and apply the fix
4. **Lab 03**: Core app challenge — build a Streamlit data product over the marts layer, with optional Gold (semantic view + chat) and Platinum (Snowflake ML) tiers
5. **Lab 04**: Optional advanced capstone — deploy and orchestrate the pipeline with Amazon MWAA
6. **Lab 05**: Instructor validation runbook

## Key CoCo Skills Used

- `sql-author` — Querying and exploring Snowflake tables
- `lineage` — Tracing data dependencies to understand the bug's impact
- `developing-with-streamlit` — Core: building the Lab 03 app challenge
- `semantic-view` — Gold bonus: defining a semantic layer over the marts
- `cortex-agent` — Gold bonus: wiring Cortex Analyst chat into the Streamlit app
- `machine-learning` — Platinum bonus: forecasting and anomaly detection via Snowflake-native ML
- `dbt-projects-on-snowflake` / dbt skill — Lab 02 debug and Lab 04 orchestration
- `dynamic-tables` — Optional: creating Dynamic Tables for real-time aggregation
