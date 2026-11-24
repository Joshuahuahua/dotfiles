# Project memory
- For this AWS infrastructure project, ask for explicit approval before making any AWS API/CLI calls or changes, including read-only inspection. Do not run Terraform apply, AWS CLI commands, or create/update/delete AWS resources without that approval. _(saved 2026-11-09)_

## Project memory
- User permits local commands and AWS CLI/API activity for this project provided the assistant first explains what it will do, whether it reads or changes AWS, and where the action/result can be observed in the AWS Console. Continue to announce AWS-facing operations before running them. _(saved 2026-11-09)_

## Project memory
- When AWS SSO credentials expire (error: "Token has expired and refresh failed"), re-authenticate using: `AWS_PROFILE=diversus_sandbox aws sso login --profile diversus_sandbox`. The browser will open for OAuth flow, or use `--remote` flag to paste code. If already configured with `[profile diversus_sandbox]` in `~/.aws/config` pointing to an expired SSO session, run `aws sso logout --profile diversus_sandbox` first, then login again. _(saved 2026-11-13)_
