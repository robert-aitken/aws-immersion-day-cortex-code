# AI-Accelerated Data Engineering with Snowflake + AWS

**Hands-On with Cortex Code CLI**

An AWS Immersion Day workshop that teaches data engineers how to use Snowflake's Cortex Code (CoCo) CLI to inspect data, run setup tasks, debug a dbt project, and validate a simple AWS-backed workshop environment.

## Recommended Scope

The core path in this repo is:

1. Connect to the EC2 jumphost and verify `cortex`, `snow`, and `aws`
2. Run Snowflake setup and load the seed data from the public workshop S3 bucket
3. Use CoCo to explore the repository, schemas, and lineage
4. Reproduce and fix the planted dbt bug, then rerun the project
5. Build a Streamlit data product on top of the clean marts layer (the **App Challenge**)

Amazon MWAA orchestration and Iceberg/Glue content remain in the repo as advanced or instructor-led extensions. They are not part of the guaranteed completion path for every participant.

## Architecture

```
                          +-----------------------+
                          |   AWS CloudFormation   |
                          |  (Workshop Provisioner) |
                          +----------+------------+
                                     |
            +------------------------+------------------------+
            |                                                 |
   +--------v--------+                              +---------v--------+
   |  EC2 Jumphost    |                              |  Amazon MWAA      |
   |  (CoCo CLI +     |                              |  (Airflow 2.9)    |
   |   Snowflake CLI  |                              |  Optional Lab 04  |
   |   + Streamlit)   |                              |                    |
   +--------+---------+                              +---------+----------+
            |                                                  |
            |  CoCo drives                                     |  Orchestrates
            |  core labs + app                                 |  the pipeline
            v                                                  v
   +--------+---------+                              +---------+----------+
   |  Snowflake        |                              |  DAG Tasks:         |
   |                    |                              |  1. Load seed data  |
   |  SOURCE_DATA       |  <---------------------------+  2. dbt run         |
   |    raw_orders      |                              |  3. dbt test        |
   |    raw_customers   |                              +--------------------+
   |    raw_products    |
   |    raw_order_items |
   |                    |
   |  STAGING           |
   |    stg_orders      |
   |    stg_customers   |
   |    stg_order_items |
   |                    |
   |  MARTS             |  <-- Streamlit App Challenge (Lab 03)
   |    fct_orders      |      + optional semantic view
   |    dim_customers   |      + optional Cortex chat
   +--------------------+      + optional Snowflake ML
```

## What You'll Build

1. **Explore source data** with CoCo CLI and inspect the Snowflake schemas created for the workshop
2. **Understand model dependencies** across the dbt project and trace lineage from source to marts
3. **Debug a broken dbt pipeline** by finding and fixing the planted column-name bug in the mart layer
4. **Build a data product** — a Streamlit app on top of the clean marts layer, with optional bonuses for a semantic view, a chat interface, and Snowflake-native ML
5. **(Optional) Orchestrate the pipeline** with Amazon MWAA as an advanced capstone

## Prerequisites

| Requirement | Notes |
|---|---|
| AWS account | Provisioned via Workshop Studio CFn template |
| Snowflake account | With Cortex Code enabled and a PAT (programmatic access token) |
| Browser | For Session Manager terminal, Streamlit app, Airflow UI, and Snowsight |

No local software installation is required. All CLI work happens on a pre-provisioned EC2 jumphost accessed via AWS Systems Manager Session Manager.

## Deployment

### Instructor-Led (Recommended)

Deploy the CloudFormation template via AWS Workshop Studio. Each participant should receive:
- An EC2 jumphost with CoCo CLI and Snowflake CLI pre-installed
- Snowflake credentials (account, user, PAT) for their demo account

The template now also stores the Snowflake credentials in AWS Secrets Manager so optional MWAA tasks can retrieve them without relying on an implicit shell variable.

`MWAA` and `Iceberg/Glue` resources are best treated as advanced extensions unless you have separately validated that the sandbox account includes the required runtime packages and credentials.

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
│   └── workshop-template.yaml   # CloudFormation: EC2 plus optional AWS extension resources
├── dags/
│   └── ecommerce_pipeline.py    # Optional MWAA DAG for advanced orchestration labs
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
│   ├── 03-from-pipeline-to-product.md
│   └── 04-deploy-and-orchestrate.md
└── scripts/
    ├── bootstrap-ec2.sh         # EC2 UserData script (tested on Amazon Linux 2023)
    ├── load-seed-data.sh        # Upload local Parquet seed files into Snowflake
    └── snowflake-setup.sql      # Create the workshop Snowflake objects
```

## Labs Overview

| Lab | Title | What You'll Do |
|---|---|---|
| 00 | Pre-Work | Connect to EC2, verify the workshop CLIs, and use a backup recovery one-liner if bootstrap failed |
| 01 | Explore and Setup | Run Snowflake setup, load seed data from public S3, and inspect the source schemas |
| 02 | Fix the Pipeline | Find and fix the dbt bug using CoCo's debugging skills |
| 03 | From Pipeline to Product | **App Challenge**: build a Streamlit data product on the marts layer; bonus tiers for semantic view, chat, and Snowflake ML |
| 04 | Deploy and Orchestrate | Advanced capstone: deploy the dbt pipeline to Amazon MWAA and run it on a schedule |

## Instructor Validation

Before the workshop, validate the paved-road flow on a fresh EC2 host and a fresh Snowflake account:

1. `scripts/bootstrap-ec2.sh` leaves `cortex`, `snow`, and `aws` available to `ec2-user`
2. `snow sql -c DEMO -q "SELECT CURRENT_ACCOUNT(), CURRENT_USER(), CURRENT_ROLE()"` succeeds without manual config edits
3. `snow sql -c DEMO -f scripts/snowflake-setup.sql` completes successfully
4. The public S3 seed-data flow loads the expected row counts consistently
5. The dbt lab fails first on the planted bug, then succeeds after the single intended fix

If you plan to run Lab 04, also validate MWAA worker dependencies, Secrets Manager access, and dbt project availability on MWAA before participants arrive.

## Dataset

E-commerce data with ~10,000 orders across 1,000 customers and 200 products. The repo includes local Parquet copies in `data/seed/`, and the core lab now loads the same files from `s3://aws-immersion-day-cortex-code-public/data/seed/`.

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
