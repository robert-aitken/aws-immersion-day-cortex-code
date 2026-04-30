# Lab 00: Pre-Work — Environment Validation

**Duration**: 10-15 minutes (self-paced, before event day)

## Objective

Before we start building, let's make sure the tools are ready. This lab confirms your EC2 jumphost, CLIs, and Snowflake connection are all working.

The jumphost is the environment that gives us a consistent way to access Cortex Code CLI across both Snowflake and AWS services. While we're using it for a clean lab experience, you can also run CoCo from any terminal — VS Code, Cursor, your local Mac/Linux/Windows shell, or even a CI/CD runner.

## Step 1: Connect to Your EC2 Jumphost

1. Log in to the AWS Console via the Workshop Studio link provided in your email
2. Navigate to **Systems Manager** > **Session Manager**
3. Click **Start session** and select the instance named `coco-workshop-jumphost`
4. You should see a terminal prompt as `ssm-user`

Switch to the workshop user:

```bash
sudo su - ec2-user
```

## Step 2: Verify CLIs

```bash
export PATH=$HOME/.local/bin:$PATH
cortex --version      # Expect: Cortex Code v1.x
snow --version        # Expect: Snowflake CLI x.x.x
aws sts get-caller-identity   # Expect: your workshop account ID
```

If either CLI is missing, the preferred path is still to ask an instructor to check the bootstrap. If you need to recover quickly, use the backup one-liner below from the `ec2-user` shell.

## Backup Recovery Path

Run this only if the host is missing `cortex` or `snow`, or if the Snowflake connection was not written correctly:

```bash
NON_INTERACTIVE=1 SKIP_PODMAN=1 SKIP_PATH_PROMPT=1 curl -LsS https://ai.snowflake.com/static/cc-scripts/install.sh | sh && pip3 install --user snowflake-cli && grep -qxF 'export PATH=$HOME/.local/bin:$PATH' ~/.bashrc || echo 'export PATH=$HOME/.local/bin:$PATH' >> ~/.bashrc && export PATH=$HOME/.local/bin:$PATH && mkdir -p ~/.snowflake && printf 'default_connection_name = "DEMO"\n\n[connections.DEMO]\naccount = "%s"\nuser = "%s"\npassword = "%s"\nrole = "COCO_WORKSHOP_ROLE"\nwarehouse = "COCO_WORKSHOP_WH"\ndatabase = "COCO_WORKSHOP"\n' "$SNOWFLAKE_ACCOUNT" "$SNOWFLAKE_USER" "$SNOWFLAKE_PAT" > ~/.snowflake/config.toml && chmod 600 ~/.snowflake/config.toml
```

Before you run it, set the three values in your shell if they are not already available from your workshop instructions:

```bash
export SNOWFLAKE_ACCOUNT="<your-account>"
export SNOWFLAKE_USER="<your-user>"
export SNOWFLAKE_PAT="<your-pat>"
```

Then re-run the normal checks:

```bash
export PATH=$HOME/.local/bin:$PATH
cortex --version
snow --version
snow sql -c DEMO -q "SELECT CURRENT_ACCOUNT(), CURRENT_USER(), CURRENT_ROLE()"
```

## Step 3: Test Snowflake Connectivity

```bash
snow sql -c DEMO -q "SELECT CURRENT_ACCOUNT(), CURRENT_USER(), CURRENT_ROLE()"
```

You should see your workshop account, user, and role.

## Step 4: Check the Workshop Repo

```bash
ls ~/workshop/
```

Expected contents: `AGENTS.md`, `cfn/`, `dags/`, `dbt_project/`, `data/`, `labs/`, `scripts/`

## What Happens Next

Lab 01 handles the Snowflake setup and seed-data load in one guided flow. In this pre-work lab, the goal is only to confirm the environment is ready for that step.

## Pre-Work Checklist

- [ ] Session Manager connects to EC2 jumphost
- [ ] `cortex --version` works
- [ ] `snow --version` works
- [ ] `aws sts get-caller-identity` works
- [ ] Workshop repo is present at `~/workshop/`
- [ ] `snow sql -c DEMO -q "SELECT CURRENT_ACCOUNT(), CURRENT_USER(), CURRENT_ROLE()"` works

## Troubleshooting

| Issue | Fix |
|---|---|
| `cortex: command not found` | Ask an instructor to check the bootstrap, or use the backup recovery path above if you need to continue immediately. |
| `snow: command not found` | Ask an instructor to check the bootstrap, or use the backup recovery path above if you need to continue immediately. |
| Snowflake connection error | Check `~/.snowflake/config.toml` exists and has correct credentials |
| Session Manager can't find instance | Wait 2-3 minutes for SSM agent to register, then refresh |

Once all checks pass, you're ready for the workshop.

---

**Next**: [Lab 01: Explore and Setup](01-explore-and-setup.md)
