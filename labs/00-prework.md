# Lab 00: Pre-Work — Environment Validation

**Duration**: 10-15 minutes (self-paced, before event day)

## Objective

Verify your EC2 jumphost is ready, confirm the workshop CLIs are already installed,
and make sure the Snowflake connection is working before you begin the core labs.

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

If either CLI is missing, stop and ask an instructor to fix the bootstrap. The paved-road workshop assumes the EC2 jumphost is already prepared.

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
| `cortex: command not found` | The EC2 bootstrap is incomplete. Ask an instructor to repair the jumphost before continuing. |
| `snow: command not found` | The EC2 bootstrap is incomplete. Ask an instructor to repair the jumphost before continuing. |
| Snowflake connection error | Check `~/.snowflake/config.toml` exists and has correct credentials |
| Session Manager can't find instance | Wait 2-3 minutes for SSM agent to register, then refresh |

Once all checks pass, you're ready for the workshop.
