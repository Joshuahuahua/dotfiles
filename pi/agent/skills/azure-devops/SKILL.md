---
name: azure-devops
description: Queries Azure DevOps work items, pull requests, and PR comments for Josh's Huddler/Hub work (org diversus, project "Huddler - Product") using a read-only PAT. Use when asked to look up a work item/ticket, query work items (assigned to me, active, current sprint, blocked), list or find pull requests (including by source branch), read PR comment threads, or "check the comments for this PR" (auto-detects current git branch).
---

# Azure DevOps

Query Azure DevOps work items, pull requests, and pull request comments for
Josh's Huddler/Hub work, using a read-only Personal Access Token (PAT).

Use this skill whenever asked to:
- Look up a work item / ticket by ID.
- Query work items (e.g. "what's assigned to me", "what's active", "what's in
  the current sprint", "what's blocked").
- List pull requests (active, completed, mine, by repo, by source branch).
- Read the comments/threads on a pull request.
- "Check the comments for this PR" / "check the comments" with no PR
  specified — detect the current git branch and find the matching open PR.
- "Open/launch this PR" (or a specific PR) in the browser.

## Configuration

- Organization: `diversus`
- Project: `Huddler - Product`
- User email (for "assigned to me" / "mine" queries): `joshua.hollander@diversus.com.au`
- API version: `7.1`

These defaults are baked into the helper script below, so no extra setup is
normally needed. They can be overridden with env vars `AZDO_ORG`,
`AZDO_PROJECT`, `AZDO_ME` if ever needed for a different org/project.

### Rule of thumb: default scope

Unless the user says otherwise:
- **Always scope to the current sprint** (`@CurrentIteration`).
- **Only include these work item types**: `Task`, `Activity`, `Sub Activity`,
  `Bug`, `Hotfix` (exclude User Stories, Features, Epics, etc.).

These defaults are built into `query` and `my-active` (pass `--all-sprints`
and/or `--all-types` to lift them for a specific request). `sprint` is
always current-sprint by definition, but still filters to the default types
unless `--all-types` is passed.

## Authentication (PAT)

The PAT is **read-only** and is kept out of git history via the dotfiles
repo's `.gitignore`:

- File: `~/.pi/agent/skills/azure-devops/.pat` (this resolves to
  `/home/josh/development/clones/dotfiles/pi/agent/skills/azure-devops/.pat`,
  since `~/.pi/agent/skills` is symlinked into the dotfiles repo). The
  dotfiles repo's `.gitignore` excludes `pi/agent/skills/azure-devops/.pat` —
  do not remove that entry.
- The helper script finds this file automatically next to itself. It also
  checks `AZDO_PAT_FILE` (custom path) and `AZDO_PAT` (inline env var) first,
  in case the token is ever needed from a different location.
- If the file still contains the placeholder `PASTE_YOUR_PAT_HERE`, the script
  will fail with a clear error — tell the user to paste their token in and
  re-run.
- Never print the PAT contents, never commit this file, never paste the token
  into chat.

## Helper script

Script: `scripts/devops.py` (resolve relative to this SKILL.md's directory,
i.e. `/home/josh/.pi/agent/skills/azure-devops/scripts/devops.py`). Run it
with `python3`. No extra dependencies (uses only the Python stdlib).

### Work items

```bash
# Get a single work item by id (full JSON)
python3 devops.py workitem 12345

# Raw WIQL WHERE clause. By default this is automatically ANDed with
# current-sprint + default-type-set filters (see "Rule of thumb" above).
python3 devops.py query "[System.State] = 'Blocked'" --top 20

# Lift the defaults when asked for something broader:
python3 devops.py query "[System.State] = 'Blocked'" --all-sprints
python3 devops.py query "[System.WorkItemType] = 'User Story'" --all-types

# Shortcut: work items assigned to Josh, state = Active, current sprint, default types
python3 devops.py my-active

# Shortcut: work items in the current sprint, default types
python3 devops.py sprint
```

`query`, `my-active`, and `sprint` print a compact one-line-per-item summary
(id, type, state, title, assignee, iteration). `workitem` prints full JSON if
more detail (description, comments, links) is needed.

### Pull requests

```bash
# Active PRs across the whole project
python3 devops.py prs

# PRs for a specific repo
python3 devops.py prs --repo hub

# Filter by status: active | completed | abandoned | all
python3 devops.py prs --status completed

# Only PRs created by Josh
python3 devops.py prs --mine

# Find a PR by its source branch (searches across all statuses automatically)
python3 devops.py prs --source-branch subscription-manager-poc

# Full JSON detail for one PR
python3 devops.py pr hub 4567
```

### Pull request comments

```bash
# All comment threads (including resolved/system) for a known repo + PR id
python3 devops.py pr-comments "Huddler - Product" 3808

# "Check the comments for this PR" (no repo/PR id known) — detects the current
# git branch (in cwd, or --path DIR if working in a different repo checkout),
# finds the matching open/draft PR, and prints only UNRESOLVED comment
# threads (skips system comments and threads marked fixed/closed/wontFix/byDesign).
python3 devops.py here
python3 devops.py here --path /home/josh/development/work/huddler/hub/workspace2
```

If no open/draft PR has the current branch as its source branch, `here`
reports that clearly instead of guessing.

Prints each comment thread with its status (active/fixed/closed/etc.), a
direct deep link to that thread (`...pullrequest/<id>?discussionId=<threadId>`),
and the non-system comments inside it, author + content.

### Open a PR in the browser

```bash
# Explicit repo + PR id
python3 devops.py open "Huddler - Product" 3808

# "Open/launch this PR" with nothing specified — detects the current git
# branch (like `here`) and opens the matching open/draft PR
python3 devops.py open
python3 devops.py open --path /home/josh/development/work/huddler/hub/workspace2
```

Prints the PR's web URL and launches it via `xdg-open` (default browser).
If no matching PR is found for the current branch, it says so instead of
guessing.

## Notes

- WIQL supports Azure DevOps macros like `@Me` and `@CurrentIteration` — the
  `my-active` and `sprint` shortcuts already use the concrete email address
  configured above so results aren't dependent on whose token is running, but
  you can use `@Me` / `@CurrentIteration` directly in a raw `query` call too.
- For custom queries beyond simple WHERE clauses (e.g. different fields),
  just call `query` with any valid WIQL WHERE clause — the tool ANDs it with
  the default sprint/type filters (unless lifted) and fixes the
  SELECT/FROM/ORDER BY parts.
- If a call fails with an HTTP 401/403, the PAT is likely missing, expired, or
  lacks the needed read scope (Work Items (Read), Code (Read) are required).
