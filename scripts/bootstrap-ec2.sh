#!/bin/bash
# EC2 UserData bootstrap script for CoCo Workshop
# Tested on Amazon Linux 2023 (x86_64) — March 2026
#
# Usage: Embed as UserData in CloudFormation EC2 resource.
# Parameters injected via CFn: SnowflakeAccount, SnowflakeUser, SnowflakePAT
#
set -ex
exec > /var/log/coco-bootstrap.log 2>&1
echo "=== CoCo Workshop Bootstrap started at $(date) ==="

# -------------------------------------------------------
# 1. System dependencies
# -------------------------------------------------------
dnf install -y python3-pip git jq

# -------------------------------------------------------
# 2. Install CoCo CLI for ec2-user
#    NON_INTERACTIVE=1 — auto-answers prompts (no /dev/tty needed in UserData)
#    SKIP_PODMAN=1     — skips Podman install (not needed for workshop)
#    SKIP_PATH_PROMPT=1 — skips PATH update prompt
# -------------------------------------------------------
su - ec2-user -c 'NON_INTERACTIVE=1 SKIP_PODMAN=1 SKIP_PATH_PROMPT=1 curl -LsS https://ai.snowflake.com/static/cc-scripts/install.sh | sh'

# -------------------------------------------------------
# 3. Install Snowflake CLI via pip
#    NOTE: There is no shell installer for Snow CLI.
#    The URL sfc-repo.snowflakecomputing.com/snowflake-cli/install.sh returns 404.
# -------------------------------------------------------
su - ec2-user -c 'pip3 install --user snowflake-cli'

# -------------------------------------------------------
# 4. Add ~/.local/bin to PATH permanently
# -------------------------------------------------------
su - ec2-user -c 'echo "export PATH=\$HOME/.local/bin:\$PATH" >> ~/.bashrc'

# -------------------------------------------------------
# 5. Clone workshop repo
# -------------------------------------------------------
su - ec2-user -c 'git clone https://github.com/snowflake-labs/aws-immersion-day-cortex-code.git ~/workshop'

# -------------------------------------------------------
# 6. Write Snowflake config.toml
#    When run via CloudFormation UserData, Fn::Sub replaces the
#    ${Param} placeholders before this script executes.
#    When run standalone, set these environment variables first:
#      export SnowflakeAccount=... SnowflakeUser=... SnowflakePAT=...
# -------------------------------------------------------
mkdir -p /home/ec2-user/.snowflake
printf 'default_connection_name = "DEMO"\n\n[connections.DEMO]\naccount = "%s"\nuser = "%s"\npassword = "%s"\nrole = "COCO_WORKSHOP_ROLE"\nwarehouse = "COCO_WORKSHOP_WH"\ndatabase = "COCO_WORKSHOP"\n' \
  "${SnowflakeAccount}" "${SnowflakeUser}" "${SnowflakePAT}" \
  > /home/ec2-user/.snowflake/config.toml

chmod 600 /home/ec2-user/.snowflake/config.toml
chown -R ec2-user:ec2-user /home/ec2-user

# -------------------------------------------------------
# 7. Verify installations
# -------------------------------------------------------
echo "=== Verifying installations ==="
su - ec2-user -c 'export PATH=$HOME/.local/bin:$PATH && cortex --version'
su - ec2-user -c 'export PATH=$HOME/.local/bin:$PATH && snow --version'
su - ec2-user -c 'du -sh ~/.local/'

echo "=== CoCo Workshop Bootstrap complete at $(date) ==="
