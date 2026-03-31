# Lab 03: Deploy and Orchestrate

**Duration**: 20-30 minutes

## Objective

Deploy the DAG to Amazon MWAA and trigger the full pipeline end-to-end.

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
# Get MWAA environment name
MWAA_ENV="coco-workshop-mwaa"

# Set variables (replace with your actual values)
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

1. **load_seed_data** — Loads Parquet from S3 into Snowflake (should take ~30s)
2. **dbt_run** — Runs all dbt models (should take ~15s)
3. **dbt_test** — Validates data quality (should take ~10s)
4. **refresh_quicksight** — Triggers SPICE refresh (should take ~30s)

If any task fails, click on the failed task and check the **Log** tab.

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
| SOURCE_DATA | RAW_ORDER_ITEMS | ~39,500 |
| STAGING | STG_ORDERS | ~10,000 |
| STAGING | STG_CUSTOMERS | ~1,000 |
| STAGING | STG_ORDER_ITEMS | ~39,500 |
| MARTS | FCT_ORDERS | ~10,000 |
| MARTS | DIM_CUSTOMERS | ~1,000 |

## What You've Learned

- How to deploy Airflow DAGs to Amazon MWAA via S3
- How to configure Airflow Variables via the MWAA REST API
- How an orchestrated pipeline flows: load → transform → test → publish
- How to monitor and debug Airflow DAG runs
