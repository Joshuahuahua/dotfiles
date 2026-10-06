---
name: devops-workitem-update
description: Updates fields (state, assignee, title, description, iteration, area, tags) on an existing, real Azure DevOps work item, gated behind a mandatory user confirmation dialog enforced by the skill-confirm-gate extension. Use when the user asks to change a devops ticket/work item's state (e.g. "move to Code Review", "set it to Active"), reassign it, or edit its fields - not for creating or deleting work items (use devops-workitem-create / devops-workitem-delete for those).
metadata:
  requires-confirmation: true
---

# DevOps Work Item Update

This skill updates fields on an **existing, real** Azure DevOps work item
using the `azure-devops` skill's PAT (which has Work Items Write scope). It
is gated by `metadata.requires-confirmation: true` above: the
`~/.pi/agent/extensions/skill-confirm-gate.ts` extension intercepts any
bash command referencing this skill's directory and holds it for a real
`ctx.ui.confirm()` dialog before it runs. If the user declines, the tool
call is blocked and `bin/update.sh` never executes - nothing is changed.

## Workflow

1. Work out which work item id(s) to update and which fields are changing
   (state, assignee, title, description, iteration, area, tags). If the id
   wasn't given explicitly (e.g. "those tickets I just made"), resolve it
   from context rather than guessing - look it up with the `azure-devops`
   skill's `workitem <id>` command first if there's any doubt about which
   item or its current field values.
2. Tell the user exactly what you're about to change (id, and each
   field/new-value) before running the command - the confirm dialog only
   shows the raw bash command, so make sure your chat message is equally
   clear. For multiple work items, list all of them.
3. Run the helper script from this skill's directory so the confirm gate's
   path-matching triggers - once per work item id:

```bash
cd ~/.pi/agent/skills/devops-workitem-update && ./bin/update.sh <id> \
  [--state "<state>"] [--title "<text>"] [--description "<text>"] \
  [--assigned-to <email>] [--iteration "<path>"] [--area "<path>"] \
  [--tags "a; b"]
```

At least one field option is required. Only the fields passed are changed -
everything else on the work item is left untouched.

4. If the user approves in the dialog, the script prints the updated
   field values - relay that back to the user. If declined, tell them it
   was cancelled and nothing was changed.

## Notes

- This performs a real, live write to Azure DevOps. Don't guess a state
  name, iteration path, or area path you aren't confident about - ask the
  user rather than inventing a value. State names are project/work-item-type
  specific (e.g. "Code Review" may not be a valid state for every work item
  type) - if unsure, look the item up first and check its current state's
  workflow options, or ask the user to confirm.
- This is for **updating fields on an item that already exists**. Use
  `devops-workitem-create` to create a new one, or `devops-workitem-delete`
  to remove one - don't reach for this skill for either of those.
- The actual API call lives in the `azure-devops` skill's
  `scripts/devops.py` (`workitem-update` command) - this skill is a thin,
  confirmation-gated wrapper around it. See that skill's SKILL.md for the
  broader `devops.py` command reference.
