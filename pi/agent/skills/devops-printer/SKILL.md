---
name: devops-printer
description: Prints Azure DevOps work items, notes, todo lists, and blocker notices to Josh's thermal receipt printer. Use whenever asked to "print" a devops ticket (by id or by description), print/create a note, print a todo list, or print a blocker notice. If the ticket is described rather than given by id, use the azure-devops skill to find the matching work item id first.
---

# DevOps Printer

CLI project: `/home/josh/development/personal/devopsPrinter` (package
`devops-printer-poc`). Prints things to a physical 80mm thermal receipt
printer via the `pnpm devops` script (an alias for `tsx src/cli/index.ts`).

Always `cd /home/josh/development/personal/devopsPrinter` before running
these commands (or pass an equivalent cwd). Config (org/project/PAT/printer
settings) lives in that project's `.env`, already set up.

## Print a work item / ticket

```bash
pnpm devops <id> [<id> ...] [--preview] [--detailed] [--simple]
```

- Accepts one or more numeric work item ids — each gets its own printed
  receipt (title, state, assignee, etc. pulled live from Azure DevOps).
- `--preview` prints to stdout instead of the physical printer (useful to
  sanity check before committing paper).
- `--detailed` / `--simple` control how much info is on the receipt.

**If the user describes a ticket instead of giving an id** (e.g. "print the
ticket about the logic app for subscription manager"), first resolve it to an
id using the `azure-devops` skill (e.g. `devops.py query "..."` or `sprint` /
`my-active`, matching on title), confirm/pick the right one, then run
`pnpm devops <id>`.

Example:
```bash
cd /home/josh/development/personal/devopsPrinter && pnpm devops 20602
```

## Print a note

```bash
pnpm devops note "<title>" "<description>" [--preview] [--detailed]
pnpm devops note "<title>" "<subtitle>" "<description>"
pnpm devops note "<heading>" "<title>" "<subtitle>" "<description>"
# or explicitly:
pnpm devops note --title "Title" --description "Description" [--heading H] [--subtitle S]
```

Positional args map by count: 1 = title only, 2 = title+description, 3 =
title+subtitle+description, 4+ = heading+title+subtitle+description (extra
words join into description).

## Print a todo list

```bash
pnpm devops todo "<item text>" <ticket-id> "<another item>" ... [--preview] [--detailed]
```

- Mix free-text items and numeric Azure DevOps ticket ids in any order —
  ticket ids are automatically looked up and printed with their title.
- Every item prints with a `[ ]` checkbox. Header is `TODO`, subtitle is the
  current date, no title.

Example:
```bash
pnpm devops todo "Review that PR" 20606 "do this thing" 20607 20608
```

## Print a blocker notice

```bash
pnpm devops blocker "<title>" "<description>" [--preview] [--detailed]
```

Header is `BLOCKER`, subtitle is the current date.

## Notes

- Always `cd` into the project dir first, or the `pnpm devops` script won't
  be found.
- `--preview` is a safe way to test any of the above without wasting paper —
  use it if unsure of formatting before actually printing.
- Full CLI help: `pnpm devops --help`.
- If asked to "print" something without specifying which kind (ticket, note,
  todo, blocker), infer from context; if genuinely ambiguous, ask.
