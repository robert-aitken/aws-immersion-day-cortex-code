# Lab 05: Instructor Validation Runbook

Use this runbook before the workshop. The goal is to verify the paved-road participant experience on a fresh AWS sandbox and a fresh Snowflake workshop account.

## Required Core Checks

Run these checks in order on a newly provisioned EC2 jumphost.

1. Verify bootstrap output.

```bash
sudo cat /var/log/coco-bootstrap.log
```

Confirm that `cortex`, `snow`, and the workshop repo were installed for `ec2-user`.

2. Verify the three workshop CLIs.

```bash
sudo su - ec2-user
export PATH=$HOME/.local/bin:$PATH
cortex --version
snow --version
aws sts get-caller-identity
```

3. Verify the preconfigured Snowflake connection.

```bash
snow sql -c DEMO -q "SELECT CURRENT_ACCOUNT(), CURRENT_USER(), CURRENT_ROLE()"
```

This should succeed without editing `~/.snowflake/config.toml`.

4. Run the workshop Snowflake setup.

```bash
cd ~/workshop
snow sql -c DEMO -f scripts/snowflake-setup.sql
```

5. Load seed data and confirm row counts.

```bash
./scripts/load-seed-data.sh
```

Expected counts:

| Table | Rows |
|---|---|
| `RAW_CUSTOMERS` | ~1,000 |
| `RAW_PRODUCTS` | ~200 |
| `RAW_ORDERS` | ~10,000 |
| `RAW_ORDER_ITEMS` | ~35,000 |

6. Validate the dbt bug/fix flow.

Ask CoCo to run dbt from `dbt_project/`, confirm the initial failure on `fct_orders`, apply the single intended fix, and rerun until the project succeeds.

## Optional Advanced Checks

Run these only if you intend to include Lab 04 (MWAA orchestration). Lab 03 (the Streamlit app challenge) runs entirely on the jumphost and Snowflake, so no extra infrastructure checks are needed beyond the core path above.

1. Verify the MWAA environment imports the DAG without provider or package errors.
2. Verify MWAA workers have access to `snow`, `dbt`, the dbt project, and Snowflake credentials.
3. Verify every Airflow Variable referenced by `dags/ecommerce_pipeline.py` is present.
4. Trigger the DAG once and confirm `load_seed_data`, `dbt_run`, and `dbt_test` succeed without worker-side surgery. (Any legacy `refresh_quicksight` task should be removed or ignored — QuickSight is no longer part of the workshop.)

## Failure Checklist

Stop the workshop rollout if any of the following are true:

- `cortex` or `snow` is missing on the jumphost
- the `DEMO` Snowflake connection needs manual repair
- `scripts/snowflake-setup.sql` fails because the account is not pre-prepared
- `scripts/load-seed-data.sh` produces row counts that differ from the lab docs
- the dbt project does not fail first on the planted bug
- MWAA workers do not have Snowflake auth, `snow`, or `dbt`
- the MWAA environment is missing required provider packages
- the CloudFormation stack still leaves a placeholder trust policy that participants must understand in detail

## Recommended Participant Scope

Treat this as the guaranteed path for all participants:

1. Lab 00: environment validation
2. Lab 01: Snowflake setup, seed load, and repo exploration
3. Lab 02: dbt bug investigation and fix
4. Lab 03: From Pipeline to Product — Streamlit app challenge over the marts layer

Treat Lab 04 (MWAA orchestration) as advanced or instructor-led unless the advanced checks above have been completed successfully.