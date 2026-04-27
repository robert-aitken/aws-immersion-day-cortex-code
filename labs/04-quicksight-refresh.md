# Lab 04: QuickSight Refresh

**Duration**: 20-30 minutes

## Objective

This is an advanced lab. Use it only if an instructor has already confirmed that QuickSight is enabled in the workshop account and that the dataset referenced by the orchestration flow already exists.

Verify the QuickSight SPICE dataset was refreshed by the pipeline, then build a simple dashboard.

## Step 1: Check the SPICE Refresh

If the `refresh_quicksight` task succeeded in Lab 03, the SPICE dataset has fresh data. Verify:

```bash
AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)

aws quicksight list-ingestions \
  --aws-account-id $AWS_ACCOUNT \
  --data-set-id coco-workshop-dataset \
  --region us-west-2
```

Look for an ingestion with status `COMPLETED`.

## Step 2: Open QuickSight

1. Navigate to **Amazon QuickSight** in the AWS Console
2. You should not need to self-register QuickSight during the workshop. If you are prompted to sign up, stop and ask an instructor to confirm the account setup.
3. Go to **Datasets** — you should see the `coco-workshop-dataset` with recent data

## Step 3: Create a New Analysis

1. Click the workshop dataset
2. Click **Create analysis**
3. QuickSight opens the analysis editor

## Step 4: Build a Revenue Trend Chart

1. From the **Fields list**, drag `order_date` to the X-axis
2. Drag `order_total` to the Value well
3. Change the aggregation to **Sum**
4. Set the date granularity to **Month**
5. You should see a monthly revenue trend across 2023-2024

## Step 5: Add a Top Customers Bar Chart

1. Click **Add** > **Add visual**
2. Select **Horizontal bar chart**
3. Drag `customer_name` (or `first_name` + `last_name`) to the Y-axis
4. Drag `lifetime_revenue` to the Value well
5. Sort descending by lifetime_revenue
6. Limit to top 10

## Step 6: Add a Regional Breakdown

1. Add another visual — **Donut chart**
2. Drag `region` to the **Group/Color** field
3. Drag `order_total` to **Value** (Sum)
4. You should see revenue distribution across US-EAST, US-WEST, EU-WEST, APAC, etc.

## Step 7: (Optional) Ask CoCo for Insights

Back in CoCo CLI, ask for data insights:

```
What are the top 5 product categories by revenue? And which region has the
highest average order value?
```

Compare CoCo's SQL-based answers with your QuickSight dashboard.

## Step 8: (Stretch) Create a Semantic View

Ask CoCo:

```
Create a semantic view over the marts schema that defines:
- Dimensions: customer name, region, product category, order date
- Measures: revenue, order count, average order value, lifetime value
```

This makes the data queryable via natural language through Cortex Analyst.

## What You've Learned

- How MWAA orchestration connects to QuickSight via the SPICE refresh API
- How to build basic QuickSight dashboards from Snowflake data
- The optional end-to-end extension: raw data -> dbt -> Airflow -> QuickSight
- How CoCo can provide SQL-based analytics alongside BI dashboards

## End-to-End Architecture (Completed)

```
S3 (Parquet)                    Snowflake                    AWS
────────────     ────────────────────────────     ────────────────
seed data   ──→  SOURCE_DATA (raw tables)    ──→  MWAA triggers
                      │                            the pipeline
                      ▼
                 STAGING (stg_ views)
                      │
                      ▼
                 MARTS (fct + dim tables)     ──→  QuickSight
                                                   SPICE refresh
                                                       │
                                                       ▼
                                                   Dashboard
```

If this lab worked in your environment, you validated the optional QuickSight extension on top of the core workshop path.
