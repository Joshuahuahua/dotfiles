---
name: azure-devops-pr-like
description: Likes or unlikes a specific comment on an Azure DevOps pull request (org diversus, project "Huddler - Product"). Use when asked to "like"/"unlike" a PR comment, or to check who liked one. Does nothing else - not for reading/posting comments, work items, or any other Azure DevOps action (use the azure-devops skill for those).
---

# Azure DevOps PR comment likes

A narrow, single-purpose skill: it can only like/unlike a pull request
comment (or list who liked one). It does not read work items, list PRs, or
post comments - use the `azure-devops` skill for anything else.

## Configuration

- Organization: `diversus`
- Project: `Huddler - Product`
- API version: `7.1`

Overridable with env vars `AZDO_ORG`, `AZDO_PROJECT` if ever needed.

## Authentication (PAT)

This skill reuses the **same PAT file** as the `azure-devops` skill
(`~/.pi/agent/skills/azure-devops/.pat`) rather than storing a second copy of
the secret - that token has had the **Code (Write)** scope added
specifically so the likes endpoints work. It is still a shared token, so
treat it with the same care: never print it, never commit it, never paste it
into chat.

Can be overridden with `AZDO_PAT_FILE` (custom path) or `AZDO_PAT` (inline
env var) if ever needed.

## Helper script

Script: `scripts/pr-like.py` (resolve relative to this SKILL.md's directory,
i.e. `/home/josh/.pi/agent/skills/azure-devops-pr-like/scripts/pr-like.py`).
Run it with `python3`. No extra dependencies (stdlib only).

```bash
# List comments on a PR with their thread id + comment id, so a target can
# be picked (needed since like/unlike require exact ids).
python3 pr-like.py list-comments <repo> <pr-id>

# Like a specific comment
python3 pr-like.py like <repo> <pr-id> <thread-id> <comment-id>

# Unlike a specific comment
python3 pr-like.py unlike <repo> <pr-id> <thread-id> <comment-id>

# List who has liked a specific comment
python3 pr-like.py likes <repo> <pr-id> <thread-id> <comment-id>
```

If the user doesn't give a thread/comment id directly (e.g. "like Dave's
comment on this PR"), run `list-comments` first to find the matching
thread/comment id by author and content, then confirm the target with the
user before liking if there's any ambiguity.

To find the PR itself (by branch, "this PR", etc.) use the `azure-devops`
skill's `here`/`prs`/`pr` commands - this skill assumes you already know the
repo + PR id.

## Notes

- Liking is low-stakes and reversible (unlike undoes it), so this skill does
  not route through a confirmation-gate extension like the work-item
  create/delete skills do. Still, confirm the target comment with the user
  first if it's at all ambiguous which one they mean.
- If a call fails with an HTTP 401/403, the PAT is likely missing the
  Code (Write) scope, or has expired.
