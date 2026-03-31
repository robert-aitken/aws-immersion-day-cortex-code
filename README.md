# AI-Accelerated Data Engineering with Snowflake + AWS

**Hands-On with Cortex Code CLI**

An AWS Immersion Day workshop that teaches data engineers how to build, debug, and orchestrate end-to-end data pipelines using Snowflake's Cortex Code (CoCo) CLI alongside core AWS services.

## Architecture

```
                          +-----------------------+
                          |   AWS CloudFormation   |
                          |  (Workshop Provisioner) |
                          +----------+------------+
                                     |
            +------------------------+------------------------+
            |                        |                        |
   +--------v--------+    +---------v--------+    +----------v---------+
   |  EC2 Jumphost    |    |  Amazon MWAA      |    |  Amazon QuickSight  |
   |  (CoCo CLI +     |    |  (Airflow 2.9)    |    |  (SPICE Dashboard)  |
   |   Snowflake CLI)  |    |                    |    |                     |
   +--------+---------+    +---------+----------+    +----------+----------+
            |                        |                          ^
            |  CoCo drives           |  Orchestrates            |  SPICE refresh
            |  all interactions      |  the pipeline            |  on completion
            v                        v                          |
   +--------+---------+    +---------+----------+               |
   |  Snowflake        |    |  DAG Tasks:         |               |
   |                    |    |  1. Load seed data  |               |
   |  SOURCE_DATA       |    |  2. dbt run         +---------------+
   |    raw_orders      |    |  3. dbt test        |
   |    raw_customers   |    |  4. QS refresh      |
   |    raw_products    |    +--------------------+
   |    raw_order_items |
   |                    |
   |  STAGING           |
   |    stg_orders      |
   |    stg_customers   |
   |    stg_order_items |
   |                    |
   |  MARTS             |
   |    fct_orders      |
   |    dim_customers   |
   +--------------------+
```

## What You'll Build

1. **Explore source data** with CoCo CLI — ask natural-language questions about your Snowflake schemas
2. **Debug a broken dbt pipeline** — the mart layer has a planted column-name bug that CoCo helps you find and fix
3. **Deploy and orchestrate** via Amazon MWAA — an Airflow DAG runs the full dbt build and validates results
4. **Trigger a QuickSight SPICE refresh** — the final DAG task refreshes an Amazon QuickSight dataset so dashboards reflect the latest data

## Prerequisites

| Requirement | Notes |
|---|---|
| AWS account | Provisioned via Workshop Studio CFn template |
| Snowflake account | With Cortex Code enabled and a PAT (programmatic access token) |
| Browser | For Session Manager terminal, Airflow UI, QuickSight, and Snowsight |

No local software installation is required. All CLI work happens on a pre-provisioned EC2 jumphost accessed via AWS Systems Manager Session Manager.

## Deployment

### Instructor-Led (Recommended)

Deploy the CloudFormation template via AWS Workshop Studio. Each participant receives:
- An EC2 jumphost with CoCo CLI and Snowflake CLI pre-installed
- An MWAA environment with the pipeline DAG deployed
- A QuickSight SPICE dataset connected to Snowflake
- Snowflake credentials (account, user, PAT) for their demo account

```bash
aws cloudformation deploy \
  --template-file cfn/workshop-template.yaml \
  --stack-name coco-workshop \
  --parameter-overrides \
    SnowflakeAccount=YOUR_ACCOUNT \
    SnowflakeUser=YOUR_USER \
    SnowflakePAT=YOUR_PAT \
  --capabilities CAPABILITY_NAMED_IAM
```

### Self-Paced with CoCo

Clone this repo on a machine with CoCo CLI installed and let CoCo guide you:

```bash
git clone https://github.com/snowflake-labs/aws-immersion-day-cortex-code.git
cd aws-immersion-day-cortex-code
cortex
```

CoCo will read the `AGENTS.md` file and understand the full workshop context, then walk you through each lab at your own pace.

## Repository Structure

```
.
├── AGENTS.md                    # CoCo context (read automatically by CoCo CLI)
├── README.md                    # This file
├── cfn/
│   └── workshop-template.yaml   # CloudFormation: EC2, MWAA, S3, IAM, QuickSight
├── dags/
│   └── ecommerce_pipeline.py    # Airflow DAG: dbt build -> QuickSight refresh
├── dbt_project/
│   ├── dbt_project.yml
│   ├── profiles.yml
│   ├── models/
│   │   ├── staging/             # stg_orders, stg_customers, stg_order_items
│   │   └── marts/               # fct_orders (has bug), dim_customers
│   └── tests/
├── data/
│   └── seed/                    # Parquet files: orders, customers, products, order_items
├── labs/
│   ├── 00-prework.md
│   ├── 01-explore-and-setup.md
│   ├── 02-fix-the-pipeline.md
│   ├── 03-deploy-and-orchestrate.md
│   └── 04-quicksight-refresh.md
└── scripts/
    └── bootstrap-ec2.sh         # EC2 UserData script (tested on Amazon Linux 2023)
```

## Labs Overview

| Lab | Title | What You'll Do |
|---|---|---|
| 00 | Pre-Work | Connect to EC2, verify CoCo + Snowflake CLI |
| 01 | Explore and Setup | Load seed data, explore schemas with CoCo |
| 02 | Fix the Pipeline | Find and fix the dbt bug using CoCo's debugging skills |
| 03 | Deploy and Orchestrate | Trigger the MWAA DAG, watch the pipeline run end-to-end |
| 04 | QuickSight Refresh | Verify SPICE refresh, build a simple dashboard |

## Dataset

E-commerce data with ~10,000 orders across 1,000 customers and 200 products. Provided as Parquet files in `data/seed/`.

| Table | Rows | Description |
|---|---|---|
| `raw_orders` | ~10,000 | Order headers (order_id, customer_id, order_date, status, total_amount) |
| `raw_customers` | ~1,000 | Customer records (customer_id, name, email, region, signup_date) |
| `raw_products` | ~200 | Product catalog (product_id, name, category, unit_price) |
| `raw_order_items` | ~35,000 | Line items (order_item_id, order_id, product_id, quantity, line_total) |

## Cleanup

After the workshop, delete the CloudFormation stack to remove all AWS resources:

```bash
aws cloudformation delete-stack --stack-name coco-workshop
```

Snowflake resources (database, warehouse, role) should be dropped separately via Snowsight or CoCo CLI.
