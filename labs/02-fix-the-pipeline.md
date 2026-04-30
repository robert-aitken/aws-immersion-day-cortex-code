# Lab 02: Fix the Pipeline

**Duration**: 30-40 minutes

## Objective

This is the lab where CoCo earns its keep. A broken dbt model is blocking the entire mart layer — the same kind of issue that wakes you up at 2 AM when a dashboard goes blank or an Airflow task turns red.

You'll trigger the failure, use CoCo to investigate (instead of manually grepping through SQL files), understand the cascade impact, fix it, and prove the pipeline is green. This is the debugging workflow you'll take back to your own projects.

> **Prerequisite**: Complete [Lab 01](01-explore-and-setup.md) — you need the seed data loaded and the dbt project ready.

## Step 1: Try Running dbt

If you're not already in CoCo, launch it:

```bash
cd ~/workshop
cortex -c DEMO
```

Ask CoCo to run the dbt project:

```
Run dbt against the dbt_project/ directory. Use the profile in profiles.yml.
```

You should see dbt succeed on the staging models but **fail on `fct_orders`** with an error like:

```
Compilation Error in model fct_orders (models/marts/fct_orders.sql)
  invalid identifier 'TOTAL_AMOUNT'
```

The `dim_customers` model will also fail because it depends on `fct_orders`.

## Step 2: Ask CoCo to Debug

This is where CoCo shines. Instead of manually opening SQL files and tracing column names by hand, ask it to investigate:

```
My dbt pipeline failed on the fct_orders model with an invalid identifier error.
Can you investigate and tell me what's wrong?
```

CoCo will:
1. Read the `fct_orders.sql` model
2. Identify that the `final` CTE references `ot.TOTAL_AMOUNT` on the line that computes `order_total`
3. Check the `order_totals` CTE and see the column is actually named `ORDER_TOTAL`
4. Explain the mismatch

On a real project this would save you 10-20 minutes of file navigation. On a large project with dozens of CTEs and models, it saves a lot more.

## Step 3: Understand the Impact

Before fixing anything, understand what's broken downstream. This is a key practice in production incident response — you want to know the blast radius.

Ask CoCo about the downstream effects:

```
What other models are affected by this bug? Trace the lineage.
```

CoCo should explain:
- `fct_orders` fails → `dim_customers` also fails (it depends on `fct_orders`)
- Anything that sits on top of the marts layer (a Streamlit app, a semantic view, a scheduled Airflow run) breaks for the same reason
- This is a **cascade failure** from a single column-name typo

## Step 4: Fix the Bug

Ask CoCo to fix it:

```
Fix the bug in fct_orders.sql.
```

CoCo should change line in the `final` CTE from:
```sql
ot.TOTAL_AMOUNT                         as order_total,  -- BUG
```
to:
```sql
ot.ORDER_TOTAL                          as order_total,  -- FIXED
```

## Step 5: Re-run dbt

Ask CoCo:

```
Run dbt again and show me the results.
```

This time all models should succeed:
```
Completed successfully
  5 models: 5 ✓
```

## Step 6: Run dbt Tests

Ask CoCo:

```
Now run dbt test to validate data quality.
```

Expected:
```
Completed successfully
  X tests: X ✓
```

All tests should pass: unique keys, not-null constraints, and the custom `assert_order_total_positive` test.

## Step 7: Verify the Fix

Ask CoCo to check the output:

```
Show me the top 10 customers by lifetime revenue from dim_customers.
```

You should see customer data with realistic revenue figures.

## What You've Learned

- How to use CoCo to debug dbt compilation errors
- How CoCo reads SQL models, traces column references, and identifies mismatches
- The cascade effect of a single model failure in a dbt DAG
- How CoCo can fix code directly, not just explain the problem

## Next: From Pipeline to Product

You now have a clean analytics layer in `COCO_WORKSHOP.MARTS`. In **[Lab 03](03-from-pipeline-to-product.md)** you'll turn that pipeline into something a human can actually look at — a Streamlit app built with CoCo, with optional bonus tracks for a semantic view, a chat interface, and Snowflake-native ML.

If you'd rather skip ahead to orchestration, **[Lab 04](04-deploy-and-orchestrate.md)** puts the same dbt pipeline on a schedule with Amazon MWAA.

---

**Previous**: [Lab 01: Explore and Setup](01-explore-and-setup.md) | **Next**: [Lab 03: From Pipeline to Product](03-from-pipeline-to-product.md)
