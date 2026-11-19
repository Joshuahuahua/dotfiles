---
name: aws-login
metadata:
  requires-confirmation: true
---
# AWS SSO Login Skill

## Description

Authenticate to AWS using the AWS CLI `aws sso login` command. The skill accepts a single argument: the AWS profile name to use.

## Usage

```bash
pi use aws-login <profile-name>
```

The skill will:
1. Check that `aws` is installed.
2. Run `aws sso login --profile <profile-name>`.
3. Return the exit status and any output.

If you need to log out of SSO, run `aws sso logout --profile <profile-name>` manually.

## Examples

```bash
pi use aws-login diversus_sandbox
```

This will start the SSO login flow for the `diversus_sandbox` profile.

---

*No side effects other than the CLI command are performed.*
