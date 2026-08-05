---
name: standup
description: Fetches raw material (Toggl Track history + Azure DevOps tickets/PRs) for a "standup" docket, which the AI rewrites into natural English and then prints via the devops-printer. Use whenever asked to print/generate a standup, daily update, or similar.
---

# Standup Docket

Two-step workflow: fetch raw data mechanically, then have the AI rewrite it
into natural, readable English before printing. The script deliberately does
NOT do its own text rewriting/cleanup — that's the AI's job.

Depends on the `toggl-track`, `azure-devops`, and `devops-printer` skills
already being set up (tokens in place).

## Script

`scripts/standup.py` (resolve relative to this SKILL.md's directory, i.e.
`/home/josh/.pi/agent/skills/standup/scripts/standup.py`). Run with
`python3`. Imports the `azure-devops` and `toggl-track` skill scripts
directly by file path, and shells out to `pnpm devops note` in the
devopsPrinter project to actually print.

### Step 1: fetch raw data

```bash
python3 standup.py dump
```

Prints plain, readable raw data in five groups:
- Yesterday's Toggl entry descriptions (deduplicated, whitespace-tidied only
  — no rewriting).
- Today: active work items this sprint assigned to Josh (azure-devops rule of
  thumb: current sprint, types Task/Activity/Sub Activity/Bug/Hotfix, state =
  Active).
- Today: Josh's own open PRs (status active, created by him) — raw list, for
  reference only (see below for how this is split up in the final docket).
- Today: unresolved PR comment threads on Josh's own PRs where the last
  reply wasn't from him (i.e. he owes a response) — includes a preview of
  the triggering comment for context.
- Today: PRs Josh is a **reviewer** on (not his own) that need his
  attention — either he hasn't voted/reviewed yet, or there's an unresolved
  comment thread whose last reply isn't his.
- Active PRs: the subset of Josh's own open PRs that do **NOT** need his
  input right now — either no unresolved comment threads at all, or every
  unresolved thread's last reply was already from Josh.
- Blocked: work items this sprint, assigned to Josh, state = Blocked.

### Step 2: the AI rewrites it

Read the `dump` output and compose a natural-English description with four
sections, in this exact structure:

```
YESTERDAY
- <dot point, rewritten to read naturally, e.g. "Add X" -> "Added X">
- <ticket-referencing entries can stay closer to their original text>

TODAY
[ ] <ticket item>
[ ] <PR-reply-needed item>

ACTIVE PRS
- <dot point per PR that needs no input right now>

BLOCKED
- <dot point>
```

- YESTERDAY, ACTIVE PRS, and BLOCKED are plain dot points (`- `).
- TODAY is a checklist (`[ ] `) and should ONLY contain: active tickets,
  unresolved comment threads on Josh's own PRs needing a reply, and PRs
  Josh is reviewing (not his own) that need attention (not yet voted, and/or
  an unresolved thread he hasn't replied to). Do **not** list PRs that don't
  need input in TODAY — those belong in ACTIVE PRS instead. Write items
  concisely (e.g. "Reply to Alex on PR #3808 re: telemetry naming", or
  "Review PR #3861 (Amanda)"), don't include raw URLs. For a
  not-yet-voted reviewer PR with no reply needed, just say "Review PR #123
  (Author)" — don't tack on "haven't voted yet"/similar filler, it's implied
  by the word "Review". If the SAME PR has both a not-yet-voted review AND
  an unresolved reply thread, keep them as **two separate checklist
  entries** (e.g. "Review PR #3858 (Amanda)" and, on its own line, "Reply to
  Amanda on PR #3858 re: validation status") — never combine them into one
  line like "Review PR #123, also reply...".
- ACTIVE PRS lists Josh's open PRs that don't need his input right now (from
  the `dump` output's "ACTIVE PRS" group) — just for visibility, no checkbox
  since there's no action required today.
- Don't invent information — only rephrase what `dump` returned.

### Step 3: print it

```bash
python3 standup.py print --preview --detailed <<'EOF'
YESTERDAY
- ...

TODAY
[ ] ...

ACTIVE PRS
- ...

BLOCKED
- ...
EOF
```

- Reads the final description text from **stdin** (this is why a heredoc is
  used) and forwards it to the devops-printer `note` command with
  `--heading STANDUP --title Standup --subtitle <today's date>`.
- `--preview` prints to stdout instead of the physical printer — **always
  use this while testing**, or when the user hasn't explicitly asked for a
  real print yet.
- `--detailed` gives the longer receipt layout (more lines before
  truncation) — prefer this for standups since there's usually more than 12
  lines of content.
- `--title` / `--heading` can be overridden if needed, but default to
  "Standup" / "STANDUP".

## Notes

- The "mine" PR filtering is done client-side (matching
  `createdBy.uniqueName`/`displayName` against the configured user) because
  Azure DevOps' `searchCriteria.creatorId` REST parameter requires a GUID
  identity, not an email — handled by `devops.py`'s `is_me()` helper, reused
  here.
- The printer's receipt has a line budget (12 lines in short mode, 28 in
  `--detailed`); long lists can still get truncated with `...` — keep the
  rewritten wording reasonably concise.
- If asked to "print my standup" for real, run `print` without `--preview`
  after composing the text; if unsure, preview first.
