#!/usr/bin/env bash
# Updates fields on a REAL Azure DevOps work item (state, assignee, title,
# description, iteration, area, tags). Performs a live write via the
# azure-devops skill's devops.py (which has Work Items Write scope).
#
# Confirmation is NOT handled here. It's handled by the
# ~/.pi/agent/extensions/skill-confirm-gate.ts extension, which reads
# `metadata.requires-confirmation: true` from this skill's SKILL.md and
# intercepts the tool call before this script ever runs. By the time this
# script executes, the user has already approved it in a real dialog.

set -euo pipefail

DEVOPS_SCRIPT="$HOME/.pi/agent/skills/azure-devops/scripts/devops.py"

python3 "$DEVOPS_SCRIPT" workitem-update "$@"
