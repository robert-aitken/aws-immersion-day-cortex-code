# Lab 01: Explore and Setup

**Duration**: 20-30 minutes

## Objective

Use CoCo CLI to run the Snowflake setup, load the seed data, explore the workshop
repository, and understand the core dbt pipeline before you debug it.

> **Prerequisite**: You should have completed Lab 00 and confirmed the EC2 jumphost,
> CLI tools, and Snowflake connection are ready.

## Step 1: Launch CoCo CLI

From your EC2 jumphost:

```bash
cd ~/workshop
cortex -c DEMO
```

CoCo will automatically read the `AGENTS.md` file and understand the workshop context.

## Step 2: Create the Snowflake Workshop Objects

Ask CoCo to run the setup script:

```
Run the Snowflake setup script at scripts/snowflake-setup.sql using my DEMO connection.
Summarize what it creates.
```

You should end up with:

| Object | Name |
|---|---|
| Role | `COCO_WORKSHOP_ROLE` |
| Warehouse | `COCO_WORKSHOP_WH` |
| Database | `COCO_WORKSHOP` |
| Schemas | `SOURCE_DATA`, `STAGING`, `MARTS` |
| Source Tables | `RAW_CUSTOMERS`, `RAW_PRODUCTS`, `RAW_ORDERS`, `RAW_ORDER_ITEMS` |
| Stage | `seed_stage` |

## Step 3: Load Seed Data

From the repo root:

```bash
cd ~/workshop
./scripts/load-seed-data.sh
```

Expected row counts:

| Table | Rows |
|---|---|
| `RAW_CUSTOMERS` | ~1,000 |
| `RAW_PRODUCTS` | ~200 |
| `RAW_ORDERS` | ~10,000 |
| `RAW_ORDER_ITEMS` | ~35,000 |

## Step 4: Explore the Repository

Ask CoCo to explain the project:

```
What's in this repository? Walk me through the architecture.
```

CoCo should describe:
- The dbt project with staging and mart models
- The scripts that bootstrap Snowflake setup and seed-data loading
- The optional MWAA and QuickSight files that are kept for advanced labs

## Step 5: Explore the Source Data

Ask CoCo to look at the data that you just loaded:

```
How many rows are in each source table? Show me a sample of 5 rows from raw_orders.
```

Expected counts:
| Table | Rows |
|---|---|
| RAW_ORDERS | ~10,000 |
| RAW_CUSTOMERS | ~1,000 |
| RAW_PRODUCTS | ~200 |
| RAW_ORDER_ITEMS | ~35,000 |

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

- How to use CoCo CLI to run setup tasks and explore a repository
- How to load Parquet data into Snowflake via an internal stage
- The core workshop architecture: source data -> staging -> marts
- How dbt model dependencies work before you attempt the bug-fix lab
