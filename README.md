# AI-Accelerated Data Engineering with Snowflake + AWS

**Hands-On with Cortex Code CLI**

## Personal note on this fork

I completed the [Snowflake AWS Immersion Day](https://www.snowflake.com/event/aws-immersion-day-2026-05-20/) on Wednesday 20 May 2026.

This was a hands-on, CLI-led data engineering workshop focused on using Snowflake Cortex Code and Kiro CLI to work through a realistic Snowflake, dbt and AWS pipeline scenario.

The workflow was primarily driven through AI-assisted CLI tools, with Snowflake and dbt as the core data engineering environment and AWS used for pipeline orchestration.

My main takeaways were:

- using Cortex Code as a Snowflake and dbt-focused AI assistant, similar in concept to GitHub Copilot but more heavily optimised for Snowflake, SQL, dbt projects and data workflows
- loading Parquet source data from S3 into Snowflake
- building raw, staging and mart layers with dbt
- debugging a failing dbt model using AI-assisted SQL investigation and lineage-style reasoning
- deploying a Streamlit in Snowflake app on top of mart tables
- using Kiro CLI to deploy an Airflow DAG to S3 through a conversational CLI workflow

The most relevant concepts for my own work are the Snowflake and dbt workflow patterns, AI-assisted debugging, faster project onboarding, and assistant-led data engineering workflows. Although this workshop used AWS for orchestration, the same high-level patterns could be adapted to other cloud stacks, including Azure-based environments.

## What is Cortex Code?

[Cortex Code](https://docs.snowflake.com/en/user-guide/cortex-code) (CoCo) is Snowflake's AI-powered CLI for data engineering. Think of it as an always-available teammate that can read your project, query your warehouse, trace lineage, debug failing models, write code, and deploy apps — all from your terminal.

In this workshop you'll use CoCo the way you'd use it on a real team: to ramp up on an unfamiliar data project, track down a production bug, fix it, and then ship something useful on top of the clean data. By the end you'll have a working Streamlit app, and you'll know how to bring the same workflow back to your own pipelines.

## Workshop Path

| # | Lab | What you'll do | Link |
|---|---|---|---|
| 00 | **Pre-Work** | Connect to your jumphost and confirm the toolchain is ready | [labs/00-prework.md](labs/00-prework.md) |
| 01 | **Explore and Setup** | Load e-commerce data into Snowflake and get oriented in the project | [labs/01-explore-and-setup.md](labs/01-explore-and-setup.md) |
| 02 | **Fix the Pipeline** | Find and fix a dbt bug — the same kind of thing that pages you at 2 AM | [labs/02-fix-the-pipeline.md](labs/02-fix-the-pipeline.md) |
| 03 | **From Pipeline to Product** | Build a Streamlit app on the clean marts — the **App Challenge** with a prize | [labs/03-from-pipeline-to-product.md](labs/03-from-pipeline-to-product.md) |
| 04 | **Deploy and Orchestrate** | *(Advanced)* Put the pipeline on a schedule with Amazon MWAA | [labs/04-deploy-and-orchestrate.md](labs/04-deploy-and-orchestrate.md) |

Labs 00–03 are the core path every participant will complete. Lab 04 is an advanced capstone for environments where MWAA has been pre-validated by an instructor.

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

## What You'll Walk Away With

1. **A working debugging workflow** — you'll see how CoCo reads SQL, traces lineage, and fixes models without you manually grepping through files
2. **A shipped data product** — a Streamlit in Snowflake app that turns raw data into something a stakeholder can actually use
3. **Repeatable patterns** — everything here (dbt debug, semantic views, ML scoring, Airflow orchestration) maps directly to work you do on your own pipelines

## Prerequisites

| Requirement | Notes |
|---|---|
| AWS account | Provisioned via Workshop Studio CFn template |
| Snowflake account | With Cortex Code enabled and a PAT (programmatic access token) |
| Browser | For Session Manager terminal, Streamlit app, Airflow UI, and Snowsight |

No local software installation required. All CLI work happens on a pre-provisioned EC2 jumphost accessed via AWS Systems Manager Session Manager.

## Getting Started

### Instructor-Led (Recommended)

Your instructor will deploy the CloudFormation template via AWS Workshop Studio. You'll receive:
- An EC2 jumphost with CoCo CLI and Snowflake CLI pre-installed
- Snowflake credentials (account, user, PAT) for your demo account

Then head straight to [Lab 00: Pre-Work](labs/00-prework.md).

### Self-Paced

Clone this repo on a machine with CoCo CLI installed and let CoCo guide you:

```bash
git clone https://github.com/snowflake-labs/aws-immersion-day-cortex-code.git
cd aws-immersion-day-cortex-code
cortex
```

CoCo reads the `AGENTS.md` file and understands the full workshop context, then walks you through each lab at your own pace.

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

## Dataset

E-commerce data spanning 2024–2025: ~10,000 orders across 1,000 customers and 200 products, with ~35,000 line items. The data has enough depth for meaningful analytics — regional trends, customer concentration, category shifts — and a few surprises worth finding.

| Table | Rows | Description |
|---|---|---|
| `raw_orders` | ~10,000 | Order headers (order_id, customer_id, order_date, status, total_amount) |
| `raw_customers` | ~1,000 | Customer records (customer_id, name, email, region, signup_date) |
| `raw_products` | ~200 | Product catalog (product_id, name, category, unit_price) |
| `raw_order_items` | ~35,000 | Line items (order_item_id, order_id, product_id, quantity, line_total) |

Seed data lives locally in `data/seed/` and is also served from `s3://aws-immersion-day-cortex-code-public/data/seed/`.

## Instructor Validation

Before the workshop, validate the paved-road flow on a fresh EC2 host and a fresh Snowflake account:

1. `scripts/bootstrap-ec2.sh` leaves `cortex`, `snow`, and `aws` available to `ec2-user`
2. `snow sql -c DEMO -q "SELECT CURRENT_ACCOUNT(), CURRENT_USER(), CURRENT_ROLE()"` succeeds without manual config edits
3. `snow sql -c DEMO -f scripts/snowflake-setup.sql` completes successfully
4. The public S3 seed-data flow loads the expected row counts consistently
5. The dbt lab fails first on the planted bug, then succeeds after the single intended fix

If you plan to run Lab 04, also validate MWAA worker dependencies, Secrets Manager access, and dbt project availability on MWAA before participants arrive.

## Cleanup

After the workshop, delete the CloudFormation stack to remove all AWS resources:

```bash
aws cloudformation delete-stack --stack-name coco-workshop
```

Snowflake resources (database, warehouse, role) should be dropped separately via Snowsight or CoCo CLI.
