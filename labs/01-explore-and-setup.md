# Lab 01: Explore and Setup

**Duration**: 20-30 minutes

## Objective

Use CoCo CLI to explore the workshop repository, understand the pipeline architecture, and load seed data into Snowflake.

## Step 1: Launch CoCo CLI

From your EC2 jumphost:

```bash
cd ~/workshop
cortex -c DEMO
```

CoCo will automatically read the `AGENTS.md` file and understand the workshop context.

## Step 2: Explore the Repository

Ask CoCo to explain the project:

```
What's in this repository? Walk me through the architecture.
```

CoCo should describe:
- The dbt project with staging and mart models
- The MWAA DAG that orchestrates the pipeline
- The QuickSight SPICE refresh as the final step

## Step 3: Explore the Source Data Schema

Ask CoCo to look at what data we'll be working with:

```
Describe the Parquet files in data/seed/. What tables will these become in Snowflake?
```

## Step 4: Load Seed Data into Snowflake

Ask CoCo to help load the data:

```
Help me create the SOURCE_DATA schema in COCO_WORKSHOP and load the Parquet
seed files from the workshop S3 bucket. The bucket name is in the Airflow variable
workshop_bucket, but you can find it from the CloudFormation stack outputs.
```

Alternatively, run the load manually:

```bash
# Find your workshop bucket
BUCKET=$(aws cloudformation describe-stacks \
  --stack-name coco-workshop \
  --query 'Stacks[0].Outputs[?OutputKey==`WorkshopBucketName`].OutputValue' \
  --output text)
echo "Workshop bucket: $BUCKET"

# Upload seed data to S3
aws s3 sync ~/workshop/data/seed/ s3://$BUCKET/data/seed/
```

Then ask CoCo:

```
Create a Snowflake stage pointing to s3://<your-bucket>/data/seed/ and load
all four Parquet files into tables in COCO_WORKSHOP.SOURCE_DATA.
```

## Step 5: Verify the Data

Ask CoCo:

```
How many rows are in each source table? Show me a sample of 5 rows from raw_orders.
```

Expected counts:
| Table | Rows |
|---|---|
| RAW_ORDERS | ~10,000 |
| RAW_CUSTOMERS | ~1,000 |
| RAW_PRODUCTS | ~200 |
| RAW_ORDER_ITEMS | ~39,500 |

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

- How to use CoCo CLI to explore a repository and understand its architecture
- How to load Parquet data into Snowflake via stages
- The medallion architecture: source → staging → marts
- How dbt model dependencies work
