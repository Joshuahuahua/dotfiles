---
name: standup
description: Fetches raw material (Toggl Track history + Azure DevOps tickets/PRs) for a "standup" docket, which the AI rewrites into natural English and then prints via the devops-printer. Use whenever asked to print/generate a standup, daily update, or similar.
---

# Standup Docket

Two-step workflow: fetch raw data mechanically, then have the AI rewrite it into natural, readable English before printing. The script deliberately does NOT do its own text rewriting/cleanup — that is the AI's job.

Depends on the `toggl-track`, `azure-devops`, and `devops-printer` skills already being set up (tokens in place).

## Important execution rules

- This skill is the entry point for all standup requests.
- Follow this document's workflow in order. Do not substitute another skill for this workflow.
- Skills are instructions, not callable tools. Never attempt to invoke a skill name as a tool.
- Use the actual tools available in Pi to execute commands. Do not invent tool names or alternative workflows.
- Do not skip steps. Fetch the raw data, compose the docket, then print it.
- **Always print the completed docket by default.**
- Never ask for confirmation before printing. Printing is the expected final step of every standup request.
- Only use preview mode when Josh explicitly requests a preview, asks not to print, or is testing the workflow.
- Do not claim that a docket has been printed unless the print command actually succeeds.

## Script

`scripts/standup.py` (resolve relative to this SKILL.md's directory, i.e. `/home/josh/.pi/agent/skills/standup/scripts/standup.py`).

Always execute it using `python3`, never `bash` or another shell interpreter.

The script imports the `azure-devops` and `toggl-track` skill scripts directly by file path, and shells out to `pnpm devops note` in the devopsPrinter project to actually print.

### Step 1: Fetch raw data

Run:

```bash
python3 /home/josh/.pi/agent/skills/standup/scripts/standup.py dump
```

Read the complete output before composing the docket.

The script prints raw data in six groups:

- **Yesterday's Toggl entry descriptions:** Deduplicated, whitespace-tidied only (no rewriting). If today is Monday, "yesterday" means last Friday instead of Sunday. If that day has nothing tracked, the script keeps walking back one weekday at a time (skipping weekends) until it finds a day with entries, and labels the section with that day's actual name.
- **Today's Toggl entry descriptions already tracked:** Things Josh has already started/done today that should appear in TODAY too, not just planned/pending work. Same deduplication and whitespace-only treatment.
- **Today: active work items this sprint assigned to Josh:** Azure DevOps rule of thumb: current sprint, types Task/Activity/Sub Activity/Bug/Hotfix, state = Active.
- **Today: Josh's own open PRs:** Status active, created by him. Raw list, for reference only (see below for how this is split up in the final docket).
- **Today: unresolved PR comment threads on Josh's own PRs where the last reply wasn't from him:** These require a response from Josh and include a preview of the triggering comment for context.
- **Today: PRs Josh is a reviewer on (not his own) that need his attention:** Either he hasn't voted/reviewed yet, or there's an unresolved comment thread whose last reply isn't his.
- **Active PRs:** The subset of Josh's own open PRs that do NOT need his input right now — either no unresolved comment threads at all, or every unresolved thread's last reply was already from Josh.
- **Blocked:** Work items this sprint, assigned to Josh, state = Blocked.

If the script fails, inspect the actual error and address it. Do not blindly retry with different interpreters, invent module imports, or switch to an alternative workflow.

### Step 2: Rewrite the raw data

Read the `dump` output and compose a natural-English description with four sections, in this exact structure:

```text
YESTERDAY (<day name, e.g. Friday>)
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

#### YESTERDAY

- The heading must include the actual day name in brackets, taken from the dump output's `YESTERDAY (<day>)` header.
- For example, `YESTERDAY (Friday)` on a Monday or `YESTERDAY (Tuesday)` on a Wednesday.
- Use plain dot points (`- `).
- Rewrite entries naturally, generally using past tense. For example, "Add X" becomes "Added X".
- Ticket-referencing entries can stay closer to their original text.

#### TODAY

TODAY is a checklist using `[ ] `.

Include:

1. Today's already-tracked Toggl entries, rephrased naturally but kept in present/ongoing phrasing. For example, "Prep for kill switch meeting", NOT "Prepped for kill switch meeting".
2. Active tickets.
3. Unresolved comment threads on Josh's own PRs needing a reply.
4. PRs Josh is reviewing (not his own) that need attention.

PR formatting rules:

- Refer to PRs by BOTH their name and number. Include the title (shortened or summarised if long) and PR ID.
- Examples:
  - `Reply to Alex on PR #3808 re: telemetry naming`
  - `Review PR #3861: Create Library Locations Updates (Amanda)`
- Do not include raw URLs.
- For a not-yet-voted reviewer PR with no reply needed, simply say `Review PR #123: <name> (Amanda)`. Do not add filler such as "haven't voted yet" because the word "Review" already implies the required action.
- If the SAME PR has both a not-yet-voted review AND an unresolved reply thread, keep them as TWO separate checklist entries.
  - For example:
    - `Review PR #3858: build pipeline update (Amanda)`
    - `Reply to Amanda on PR #3858 re: validation status`
  - Never combine these into one checklist item.
- Do NOT list PRs that don't need Josh's input in TODAY. Those belong in ACTIVE PRS instead.
- If a single PR has many unresolved comment threads (roughly more than 2–3), don't list a separate checklist item per thread. This can exceed the printer's line budget and cause silent truncation.
- Instead, group them into one line per reviewer, e.g. `Reply to Alex on PR #3896: 6 comments (naming, types, cleanup)`. Include a few short topic keywords rather than every individual comment.

#### ACTIVE PRS

- Use plain dot points (`- `), not checkboxes.
- Include Josh's open PRs that do NOT need his input right now, using the dump's `ACTIVE PRS` group.
- This section is for visibility only. No action is required today.

#### BLOCKED

- Use plain dot points (`- `), not checkboxes.
- Include blocked work items from the dump.
- Do not invent reasons or additional context.

#### General rewriting rules

- Do not invent information. Only rephrase what the dump returned.
- Do not add assumptions, guessed progress, invented ticket details, or fabricated dates.
- Do not include sections or entries unsupported by the dump.
- Preserve the four-section structure even when a section has no entries. If empty, include its heading and leave the section empty.
- Keep the wording concise enough to fit on the printer receipt.
- Do not include raw URLs.

### Step 3: Print the docket

**Printing is mandatory by default. Do not use preview mode unless Josh explicitly requests it.**

Use the following command structure, without `--preview`:

```bash
python3 /home/josh/.pi/agent/skills/standup/scripts/standup.py print --detailed <<'EOF'
YESTERDAY (Friday)
- ...

TODAY
[ ] ...

ACTIVE PRS
- ...

BLOCKED
- ...
EOF
```

Important:

- The final description text must be passed through stdin. This is why a heredoc is used.
- The script forwards the text to the devops-printer `note` command with `--heading STANDUP --title <today's date> --subtitle ""`.
- The docket shows the STANDUP heading with the date as the title text, and no subtitle line at all.
- `--detailed` gives the longer receipt layout (more lines before truncation). Always prefer this for standups.
- `--heading` can be overridden if needed, but defaults to `STANDUP`.
- Do not manually supply or calculate the date. The printer automatically supplies today's date as the title.
- Do not ask Josh whether to print. Print automatically once the docket is composed.
- Only add `--preview` or `--no-print` when Josh explicitly requests a preview or asks not to print.
- If printing fails, report the actual error. Do not claim success.

### Step 4: Check the print result

After executing the print command:

- Check the command's exit status and output.
- If the receipt was truncated, condense the docket while preserving the important information and print it again.
- The printer's receipt has a line budget (12 lines in short mode, 28 in `--detailed`); long lists can still get truncated with `...`.
- Use the PR-reply grouping rule in Step 2 to reduce excessive lines.
- Do not silently omit important entries to fit the receipt.
- Only report that printing succeeded if the command completed successfully.

## Notes

- The "mine" PR filtering is done client-side (matching `createdBy.uniqueName`/`displayName` against the configured user) because Azure DevOps' `searchCriteria.creatorId` REST parameter requires a GUID identity. This is handled by `devops.py`'s `is_me()` helper, reused here.
- The printer's receipt has a line budget: 12 lines in short mode, 28 in `--detailed`. Long lists can still get truncated with `...`.
- The standup script deliberately retrieves raw material only. The AI is responsible for rewriting it into the required four-section format.
- Printing is the default and expected behaviour. Preview is an exception, used only when Josh explicitly asks for it or when testing.

