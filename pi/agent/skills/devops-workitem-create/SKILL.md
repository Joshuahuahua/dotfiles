---
name: devops-workitem-create
description: Creates a real Azure DevOps work item (Task, Bug, User Story, etc.), gated behind a mandatory user confirmation dialog enforced by the skill-confirm-gate extension. Use when the user asks to create/raise/file a devops ticket or work item.
metadata:
  requires-confirmation: true
---

# DevOps Work Item Create

This skill creates a **real** Azure DevOps work item using the
`azure-devops` skill's PAT (which has Work Items Write scope). It is gated
by `metadata.requires-confirmation: true` above: the
`~/.pi/agent/extensions/skill-confirm-gate.ts` extension intercepts any
bash command referencing this skill's directory and holds it for a real
`ctx.ui.confirm()` dialog before it runs. If the user declines, the tool
call is blocked and `bin/create.sh` never executes - nothing is created.

## Workflow

1. Work out the work item's fields from context: type (Task, Bug, User
   Story, etc.), title, description, and estimate (hours), plus optionally
   assignee, iteration, area path, parent id, tags. `--description` and
   `--estimate` are **required** - Azure DevOps rejects the create without
   them. Ask the user for an estimate if they haven't given one; don't
   guess it.
2. Tell the user exactly what you're about to create (type, title,
   description, estimate, and any other fields) before running the command
   - the confirm dialog only shows the raw bash command, so make sure your
   chat message is equally clear.
3. Run the helper script from this skill's directory so the confirm gate's
   path-matching triggers:

```bash
cd ~/.pi/agent/skills/devops-workitem-create && ./bin/create.sh "<type>" "<title>" --description "<text>" --estimate <hours> [--assigned-to <email>] [--iteration "<path>"] [--area "<path>"] [--parent <id>] [--tags "a; b"]
```

4. If the user approves in the dialog, the script prints the new item's id
   and web URL - relay that back to the user. If declined, tell them it was
   cancelled and nothing was created.

## Notes

- This performs a real, live write to Azure DevOps. Don't guess fields you
  aren't confident about (iteration path, area path, parent id) - ask the
  user rather than inventing a value.
- The actual API call lives in the `azure-devops` skill's
  `scripts/devops.py` (`workitem-create` command) - this skill is a thin,
  confirmation-gated wrapper around it. See that skill's SKILL.md for the
  full `workitem-create` argument reference.
