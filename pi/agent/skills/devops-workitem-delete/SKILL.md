---
name: devops-workitem-delete
description: Deletes a real Azure DevOps work item (soft-delete to the recycle bin by default), gated behind a mandatory user confirmation dialog enforced by the skill-confirm-gate extension. Use when the user asks to delete/remove a devops ticket or work item.
metadata:
  requires-confirmation: true
---

# DevOps Work Item Delete

This skill deletes a **real** Azure DevOps work item using the
`azure-devops` skill's PAT (which has Work Items Write scope). It is gated
by `metadata.requires-confirmation: true` above: the
`~/.pi/agent/extensions/skill-confirm-gate.ts` extension intercepts any
bash command referencing this skill's directory and holds it for a real
`ctx.ui.confirm()` dialog before it runs. If the user declines, the tool
call is blocked and `bin/delete.sh` never executes - nothing is deleted.

## Workflow

1. Confirm with the user which work item id to delete, and show them its
   type/title first (look it up with the `azure-devops` skill's
   `workitem <id>` command) so they're confirming a specific, known item -
   never delete an id you haven't looked up and described back to them.
2. By default this is a **soft delete** - the item moves to the project's
   recycle bin and can be recovered later. Only pass `--destroy` for a
   permanent, unrecoverable delete, and only if the user explicitly asks
   for that.
3. Run the helper script from this skill's directory so the confirm gate's
   path-matching triggers:

```bash
cd ~/.pi/agent/skills/devops-workitem-delete && ./bin/delete.sh <id> [--destroy]
```

4. If the user approves in the dialog, the script confirms the deletion. If
   declined, tell them it was cancelled and nothing was deleted.

## Notes

- This performs a real, live delete against Azure DevOps. Never call it
  speculatively or as part of "cleaning up" without the user naming the
  specific id.
- The actual API call lives in the `azure-devops` skill's
  `scripts/devops.py` (`workitem-delete` command) - this skill is a thin,
  confirmation-gated wrapper around it.
