#!/usr/bin/env bash
# Placeholder/prototype script. Performs NO real action - does not call
# Azure DevOps or any API.
#
# Confirmation is NOT handled here. It's handled by the
# ~/.pi/agent/extensions/skill-confirm-gate.ts extension, which reads
# `metadata.requires-confirmation: true` from this skill's SKILL.md and
# intercepts the tool call before this script ever runs. By the time this
# script executes, the user has already approved it in a real dialog.

set -euo pipefail

type="${1:-Task}"
title="${2:-Untitled work item}"

echo "(placeholder) Would create the work item now - no real action taken."
echo "  Type:  $type"
echo "  Title: $title"
