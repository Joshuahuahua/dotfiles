---
name: aws-login
description: Logs in to AWS via SSO for a given profile (aws sso login --profile). Use when asked to log in to AWS / SSO or refresh AWS credentials for a profile.
metadata:
  requires-confirmation: true
---
# AWS SSO Login Skill

## Description

Authenticate to AWS using the AWS CLI `aws sso login` command. The skill accepts a single argument: the AWS profile name to use.

## Usage

```bash
~/.pi/agent/skills/aws-login/run.sh <profile-name>
```

The skill will:
1. Check that `aws` is installed.
2. Run `aws sso login --profile <profile-name>`.
3. Return the exit status and any output.

If you need to log out of SSO, run `aws sso logout --profile <profile-name>` manually.

## Examples

```bash
~/.pi/agent/skills/aws-login/run.sh diversus_sandbox
```

This will start the SSO login flow for the `diversus_sandbox` profile.

---

*No side effects other than the CLI command are performed.*
