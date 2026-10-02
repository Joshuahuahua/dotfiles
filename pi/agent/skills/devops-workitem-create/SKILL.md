---
name: devops-workitem-create
description: PLACEHOLDER/PROTOTYPE - demonstrates a confirmation gate for creating Azure DevOps work items, enforced at the engine level via the skill-confirm-gate extension. Does not actually create anything yet. Use only to show the confirmation UX; do not wire this up to the real write API until the user explicitly asks for that.
metadata:
  requires-confirmation: true
---

# DevOps Work Item Create (placeholder)

This skill is a **placeholder**. It exists only to demonstrate what a
confirm-before-write flow looks like. It does **not** call Azure DevOps and
cannot create, edit, or delete anything yet - the azure-devops skill's PAT
is read-only, and this script has no network calls at all.

The `metadata.requires-confirmation: true` field above is read by the
`~/.pi/agent/extensions/skill-confirm-gate.ts` extension, not by this
skill's own script. That extension hooks Pi's `tool_call` event and holds
any bash command that references this skill's directory until the user
answers a real confirm dialog (`ctx.ui.confirm()`, shown by Pi's own UI). If
declined, the tool call is blocked with `{ block: true }` before it runs -
the agent cannot make it proceed by retrying, picking a different script,
or hand-rolling the command, because the gate sits at the engine's tool
layer, not inside a script the agent chooses whether to call.

This is stronger than a script popping its own GUI dialog (an earlier
version of this skill did that with zenity): a script-level dialog only
gates that one script, and relies on the agent actually choosing to run it
instead of some other path to the same effect. The extension-level gate
intercepts the tool call itself, regardless of which script constructed it.

## When to use

Only when the user is testing/demoing the confirmation flow for creating a
work item. Do not treat this as a real "create ticket" capability.

## Workflow

1. Gather the proposed work item fields from context (type, title,
   description, etc).
2. Show the user exactly what would be created.
3. Run the helper script. The skill-confirm-gate extension will intercept
   the call and show the real confirm dialog before it executes.

```bash
cd ~/.pi/agent/skills/devops-workitem-create && ./bin/create.sh "<type>" "<title>"
```

If the user declines in the dialog, the tool call is blocked and the
script body never runs - tell the user it was cancelled.

## Notes

- Real implementation would need: a PAT with Work Items (Write) scope, a
  `workitem create` command added to the azure-devops skill's
  `scripts/devops.py`, and `metadata.requires-confirmation: true` added to
  that command's invoking skill (or a dedicated skill) so the same gate
  covers it.
- Do not add write scope or real creation logic to this skill without the
  user explicitly asking for it.
