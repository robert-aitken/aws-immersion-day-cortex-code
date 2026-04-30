# Lab 04: Deploy and Orchestrate Your Pipeline with Airflow

**Duration**: 20-30 minutes

> **Prerequisite**: Complete [Lab 02](02-fix-the-pipeline.md) (fixed dbt pipeline) and ideally [Lab 03](03-from-pipeline-to-product.md) (Streamlit app). This lab is an advanced capstone for environments where an instructor has validated MWAA.

## Objective

In the real world, nobody runs `dbt run` by hand forever. Once your pipeline works, you schedule it so data flows automatically. This lab puts the fixed dbt pipeline on a schedule using Amazon MWAA (Managed Workflows for Apache Airflow) — the same orchestration pattern used in production environments.

You'll upload the DAG, wire up the Airflow Variables, trigger a run, and watch it complete.

## Before You Start

Do not assume the CloudFormation stack is sufficient on its own. Confirm all of the following first:

- The MWAA environment has the required Python packages and providers installed
- The MWAA workers can access the workshop repo or a packaged copy of the dbt project
- Snowflake credentials are available to MWAA without manual worker-side edits (Secrets Manager is the recommended path)

If any of these are missing, stop here and treat this as instructor-only content.

## Pipeline Overview

The DAG in `dags/ecommerce_pipeline.py` runs three tasks in sequence:

1. `load_seed_data` — Copies Parquet files from S3 to the Snowflake source tables
2. `dbt_run` — Executes `dbt run` against the dbt project
3. `dbt_test` — Runs `dbt test` to validate data quality

This is exactly the flow you ran by hand in Labs 01 and 02, just scheduled and observable.

## Step 1: Upload the DAG to MWAA

The MWAA environment reads DAGs from the workshop S3 bucket. Upload the fixed pipeline:

```bash
# Find your workshop bucket
BUCKET=$(aws cloudformation describe-stacks \
  --stack-name coco-workshop \
  --query 'Stacks[0].Outputs[?OutputKey==`WorkshopBucketName`].OutputValue' \
  --output text)

# Upload the DAG
aws s3 cp ~/workshop/dags/ecommerce_pipeline.py s3://$BUCKET/dags/
echo "DAG uploaded to s3://$BUCKET/dags/"
```

Or ask CoCo:

```
Upload the ecommerce_pipeline DAG to the MWAA S3 bucket. The bucket name
is in the CloudFormation stack outputs for coco-workshop.
```

## Step 2: Set Airflow Variables

The DAG reads configuration from Airflow Variables. Set them via the AWS CLI:

```bash
MWAA_ENV="coco-workshop-mwaa"

aws mwaa invoke-rest-api \
  --name $MWAA_ENV \
  --method POST \
  --path "/variables" \
  --body '{"key": "snowflake_account", "value": "YOUR_ACCOUNT"}'

aws mwaa invoke-rest-api \
  --name $MWAA_ENV \
  --method POST \
  --path "/variables" \
  --body '{"key": "snowflake_user", "value": "YOUR_USER"}'

aws mwaa invoke-rest-api \
  --name $MWAA_ENV \
  --method POST \
  --path "/variables" \
  --body "{\"key\": \"workshop_bucket\", \"value\": \"$BUCKET\"}"

aws mwaa invoke-rest-api \
  --name $MWAA_ENV \
  --method POST \
  --path "/variables" \
  --body '{"key": "aws_account_id", "value": "YOUR_AWS_ACCOUNT_ID"}'

aws mwaa invoke-rest-api \
  --name $MWAA_ENV \
  --method POST \
  --path "/variables" \
  --body '{"key": "aws_region", "value": "us-west-2"}'
```

## Step 3: Open the Airflow UI

1. Go to the **MWAA Console URL** from the CloudFormation outputs
2. Click **Open Airflow UI**
3. Find the `ecommerce_pipeline` DAG in the list
4. Enable the DAG (toggle the switch)

## Step 4: Trigger the DAG

In the Airflow UI:

1. Click the **play** button next to `ecommerce_pipeline`
2. Click **Trigger DAG**

Or via CLI:

```bash
aws mwaa invoke-rest-api \
  --name $MWAA_ENV \
  --method POST \
  --path "/dags/ecommerce_pipeline/dagRuns" \
  --body '{"conf": {}}'
```

## Step 5: Monitor Execution

Watch the DAG run in the Airflow UI:

1. **load_seed_data** — Loads Parquet from S3 into Snowflake (~30s)
2. **dbt_run** — Runs all dbt models (~15s)
3. **dbt_test** — Validates data quality (~10s)

If any task fails, click the failed task and check the **Log** tab.

Expected high-risk failure modes in unprepared environments:

- `snow: command not found`
- `dbt: command not found`
- missing Snowflake config or password on the MWAA worker
- missing Airflow Variables

Success for this lab ends at `dbt_test`. The DAG is a 3-task pipeline.

## Step 6: Verify in Snowflake

Ask CoCo:

```
Show me a summary of what's in each schema in COCO_WORKSHOP.
How many rows are in the mart tables?
```

Expected:

| Schema | Table | Rows |
|---|---|---|
| SOURCE_DATA | RAW_ORDERS | ~10,000 |
| SOURCE_DATA | RAW_CUSTOMERS | ~1,000 |
| SOURCE_DATA | RAW_PRODUCTS | ~200 |
| SOURCE_DATA | RAW_ORDER_ITEMS | ~35,000 |
| STAGING | STG_ORDERS | ~10,000 |
| STAGING | STG_CUSTOMERS | ~1,000 |
| STAGING | STG_ORDER_ITEMS | ~35,000 |
| MARTS | FCT_ORDERS | ~10,000 |
| MARTS | DIM_CUSTOMERS | ~1,000 |

## What You've Learned

- How to validate whether an MWAA environment is actually ready for workshop use
- How to deploy Airflow DAGs to Amazon MWAA via S3
- How to configure Airflow Variables via the MWAA REST API
- How to monitor and debug Airflow DAG runs
- How to put the dbt pipeline you fixed earlier on a schedule

## End-to-End Architecture (Completed)

```
S3 (Parquet)                    Snowflake                     Orchestration
────────────     ────────────────────────────     ─────────────────────────
seed data   ──→  SOURCE_DATA (raw tables)    ──→  MWAA triggers the
                      │                           pipeline on schedule
                      ▼
                 STAGING (stg_ views)
                      │
                      ▼
                 MARTS (fct + dim tables)     ──→  Streamlit app
                                                   (from Lab 03)
```

---

**Previous**: [Lab 03: From Pipeline to Product](03-from-pipeline-to-product.md)
