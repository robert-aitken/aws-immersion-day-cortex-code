# Lab 00: Pre-Work — Environment Validation

**Duration**: 10-15 minutes (self-paced, before event day)

## Objective

Verify your EC2 jumphost is ready and all tools are working.

## Step 1: Connect to Your EC2 Jumphost

1. Log in to the AWS Console via the Workshop Studio link provided in your email
2. Navigate to **Systems Manager** > **Session Manager**
3. Click **Start session** and select the instance named `coco-workshop-jumphost`
4. You should see a terminal prompt as `ssm-user`

Switch to the workshop user:

```bash
sudo su - ec2-user
```

## Step 2: Verify CoCo CLI

```bash
cortex --version
```

Expected output:
```
Cortex Code v1.0.x
```

## Step 3: Verify Snowflake CLI

```bash
snow --version
```

Expected output:
```
Snowflake CLI version: x.x.x
```

## Step 4: Test Snowflake Connectivity

```bash
snow sql -c DEMO -q "SELECT CURRENT_ACCOUNT(), CURRENT_USER(), CURRENT_ROLE()"
```

You should see your workshop account, user, and `COCO_WORKSHOP_ROLE`.

## Step 5: Verify AWS CLI

```bash
aws sts get-caller-identity
```

You should see your workshop AWS account ID.

## Step 6: Check the Workshop Repo

```bash
ls ~/workshop/
```

You should see: `AGENTS.md`, `README.md`, `cfn/`, `dags/`, `dbt_project/`, `data/`, `labs/`, `scripts/`

## Pre-Work Checklist

- [ ] Session Manager connects to EC2 jumphost
- [ ] `cortex --version` works
- [ ] `snow --version` works
- [ ] Snowflake query returns account info
- [ ] `aws sts get-caller-identity` works
- [ ] Workshop repo is present at `~/workshop/`

## Troubleshooting

| Issue | Fix |
|---|---|
| `cortex: command not found` | Run `export PATH=$HOME/.local/bin:$PATH` and retry |
| Snowflake connection error | Check `~/.snowflake/config.toml` exists and has correct credentials |
| Session Manager can't find instance | Wait 2-3 minutes for SSM agent to register, then refresh |

Once all checks pass, you're ready for the workshop.
