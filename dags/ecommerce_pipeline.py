"""
ecommerce_pipeline.py — CoCo Workshop MWAA DAG

Orchestrates the full e-commerce data pipeline:
  1. Load seed data from S3 Parquet files into Snowflake source tables
  2. Run dbt models (staging + marts)
  3. Run dbt tests
  4. Refresh the QuickSight SPICE dataset

Deployed to MWAA via S3: s3://<workshop-bucket>/dags/ecommerce_pipeline.py
"""

from datetime import datetime, timedelta
import json

import boto3
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.providers.amazon.aws.operators.quicksight import (
    QuickSightCreateIngestionOperator,
)
from airflow.models import Variable

# ---------------------------------------------------------------------------
# Configuration — set these as Airflow Variables or override via DAG conf
# ---------------------------------------------------------------------------
SNOWFLAKE_ACCOUNT = Variable.get("snowflake_account", default_var="your-account")
SNOWFLAKE_USER = Variable.get("snowflake_user", default_var="your-user")
SNOWFLAKE_DATABASE = Variable.get("snowflake_database", default_var="COCO_WORKSHOP")
SNOWFLAKE_WAREHOUSE = Variable.get("snowflake_warehouse", default_var="COCO_WORKSHOP_WH")
SNOWFLAKE_ROLE = Variable.get("snowflake_role", default_var="COCO_WORKSHOP_ROLE")
WORKSHOP_BUCKET = Variable.get("workshop_bucket", default_var="coco-workshop-bucket")
AWS_ACCOUNT_ID = Variable.get("aws_account_id", default_var="000000000000")
QS_DATASET_ID = Variable.get("quicksight_dataset_id", default_var="coco-workshop-dataset")
AWS_REGION = Variable.get("aws_region", default_var="us-west-2")
PUBLIC_SEED_BUCKET = Variable.get("public_seed_bucket", default_var="aws-immersion-day-cortex-code-public")
SNOWFLAKE_SECRET_ID = Variable.get(
    "snowflake_secret_id",
    default_var="coco-workshop/snowflake/coco-workshop",
)


def get_snowflake_credentials():
    secrets_client = boto3.client("secretsmanager", region_name=AWS_REGION)
    secret_value = secrets_client.get_secret_value(SecretId=SNOWFLAKE_SECRET_ID)
    return json.loads(secret_value["SecretString"])


SNOWFLAKE_CREDS = get_snowflake_credentials()

# ---------------------------------------------------------------------------
# SQL to load seed data from S3 stage into Snowflake
# ---------------------------------------------------------------------------
LOAD_SEED_SQL = f"""
-- Create schema if not exists
CREATE SCHEMA IF NOT EXISTS {SNOWFLAKE_DATABASE}.SOURCE_DATA;

-- Create file format for Parquet
CREATE OR REPLACE FILE FORMAT {SNOWFLAKE_DATABASE}.SOURCE_DATA.parquet_format
  TYPE = PARQUET;

-- Create stage pointing to the workshop S3 bucket
CREATE OR REPLACE STAGE {SNOWFLAKE_DATABASE}.SOURCE_DATA.workshop_stage
  URL = 's3://{PUBLIC_SEED_BUCKET}/data/seed/'
  FILE_FORMAT = {SNOWFLAKE_DATABASE}.SOURCE_DATA.parquet_format;

-- Load raw_customers
CREATE OR REPLACE TABLE {SNOWFLAKE_DATABASE}.SOURCE_DATA.RAW_CUSTOMERS AS
SELECT
  $1:customer_id::INT           AS customer_id,
  $1:first_name::VARCHAR        AS first_name,
  $1:last_name::VARCHAR         AS last_name,
  $1:email::VARCHAR             AS email,
  $1:region::VARCHAR            AS region,
  $1:signup_date::VARCHAR       AS signup_date
FROM @{SNOWFLAKE_DATABASE}.SOURCE_DATA.workshop_stage/raw_customers.parquet;

-- Load raw_products
CREATE OR REPLACE TABLE {SNOWFLAKE_DATABASE}.SOURCE_DATA.RAW_PRODUCTS AS
SELECT
  $1:product_id::INT            AS product_id,
  $1:product_name::VARCHAR      AS product_name,
  $1:category::VARCHAR          AS category,
  $1:unit_price::DECIMAL(10,2)  AS unit_price
FROM @{SNOWFLAKE_DATABASE}.SOURCE_DATA.workshop_stage/raw_products.parquet;

-- Load raw_orders
CREATE OR REPLACE TABLE {SNOWFLAKE_DATABASE}.SOURCE_DATA.RAW_ORDERS AS
SELECT
  $1:order_id::INT              AS order_id,
  $1:customer_id::INT           AS customer_id,
  $1:order_date::VARCHAR        AS order_date,
  $1:status::VARCHAR            AS status,
  $1:total_amount::DECIMAL(12,2) AS total_amount,
  $1:created_at::VARCHAR        AS created_at
FROM @{SNOWFLAKE_DATABASE}.SOURCE_DATA.workshop_stage/raw_orders.parquet;

-- Load raw_order_items
CREATE OR REPLACE TABLE {SNOWFLAKE_DATABASE}.SOURCE_DATA.RAW_ORDER_ITEMS AS
SELECT
  $1:order_item_id::INT         AS order_item_id,
  $1:order_id::INT              AS order_id,
  $1:product_id::INT            AS product_id,
  $1:quantity::INT              AS quantity,
  $1:line_total::DECIMAL(12,2)  AS line_total
FROM @{SNOWFLAKE_DATABASE}.SOURCE_DATA.workshop_stage/raw_order_items.parquet;
"""

# ---------------------------------------------------------------------------
# DAG Definition
# ---------------------------------------------------------------------------
default_args = {
    "owner": "coco-workshop",
    "depends_on_past": False,
    "email_on_failure": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="ecommerce_pipeline",
    default_args=default_args,
    description="CoCo Workshop: E-commerce pipeline with dbt + QuickSight refresh",
    schedule_interval=None,  # Manually triggered
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["coco-workshop", "dbt", "quicksight"],
) as dag:

    # Task 1: Load seed data from S3 into Snowflake
    load_seed_data = BashOperator(
        task_id="load_seed_data",
        bash_command=f"""
            export PATH=$HOME/.local/bin:$PATH
            mkdir -p $HOME/.snowflake
            printf 'default_connection_name = "DEMO"\n\n[connections.DEMO]\naccount = "%s"\nuser = "%s"\npassword = "%s"\nrole = "%s"\nwarehouse = "%s"\ndatabase = "%s"\n' \
              '{SNOWFLAKE_CREDS["account"]}' '{SNOWFLAKE_CREDS["user"]}' '{SNOWFLAKE_CREDS["password"]}' \
              '{SNOWFLAKE_CREDS["role"]}' '{SNOWFLAKE_CREDS["warehouse"]}' '{SNOWFLAKE_CREDS["database"]}' \
              > $HOME/.snowflake/config.toml
            chmod 600 $HOME/.snowflake/config.toml
            snow sql -c DEMO -q "{LOAD_SEED_SQL.replace(chr(10), ' ')}"
        """,
    )

    # Task 2: Run dbt models (staging + marts)
    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"""
            export PATH=$HOME/.local/bin:$PATH
            cd ~/workshop/dbt_project
            export SNOWFLAKE_ACCOUNT='{SNOWFLAKE_CREDS["account"]}'
            export SNOWFLAKE_USER='{SNOWFLAKE_CREDS["user"]}'
            export SNOWFLAKE_PASSWORD='{SNOWFLAKE_CREDS["password"]}'
            dbt run --profiles-dir . --project-dir .
        """,
    )

    # Task 3: Run dbt tests
    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"""
            export PATH=$HOME/.local/bin:$PATH
            cd ~/workshop/dbt_project
            export SNOWFLAKE_ACCOUNT='{SNOWFLAKE_CREDS["account"]}'
            export SNOWFLAKE_USER='{SNOWFLAKE_CREDS["user"]}'
            export SNOWFLAKE_PASSWORD='{SNOWFLAKE_CREDS["password"]}'
            dbt test --profiles-dir . --project-dir .
        """,
    )

    # Task 4: Refresh QuickSight SPICE dataset
    refresh_quicksight = QuickSightCreateIngestionOperator(
        task_id="refresh_quicksight",
        data_set_id=QS_DATASET_ID,
        ingestion_id="{{ ts_nodash }}-coco-workshop",
        ingestion_type="FULL_REFRESH",
        wait_for_completion=True,
        check_interval=15,
        aws_conn_id="aws_default",
        region=AWS_REGION,
    )

    # Task dependencies
    load_seed_data >> dbt_run >> dbt_test >> refresh_quicksight
