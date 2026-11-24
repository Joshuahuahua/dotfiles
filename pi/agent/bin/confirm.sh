#!/usr/bin/env bash
# Shared confirmation helper for skills.
#
# Pops a real GUI yes/no dialog on the user's desktop (zenity) and blocks
# until they click. This is the only reliable way for a skill invoked by
# the agent (via a non-interactive shell call) to get an actual manual
# choice from the user - a stdin "read -p" prompt in a script the agent
# runs is answered by the agent, not the user, since the agent has no
# shared TTY with them.
#
# Usage:
#   confirm.sh "Title" "Question text" [timeout_seconds]
#
# Exit codes:
#   0   user clicked Yes/OK
#   1   user clicked No/Cancel, closed the dialog, or no GUI tool was
#       available at all
#   2   timed out waiting for a response (no answer within timeout)
#
# Falls back to xmessage if zenity isn't installed. If neither is
# available, fails safe (exit 1 = treated as "no").

set -euo pipefail

title="${1:-Confirm}"
text="${2:-Proceed?}"
timeout_seconds="${3:-120}"

if command -v zenity >/dev/null 2>&1; then
  set +e
  zenity --question \
    --title="$title" \
    --text="$text" \
    --timeout="$timeout_seconds" \
    --width=350
  code=$?
  set -e
  case "$code" in
    0) exit 0 ;;   # Yes
    5) exit 2 ;;   # zenity timeout
    *) exit 1 ;;   # No / cancelled / closed
  esac
elif command -v xmessage >/dev/null 2>&1; then
  set +e
  timeout "$timeout_seconds" xmessage -center -buttons Yes:0,No:1 "$title: $text"
  code=$?
  set -e
  if [ "$code" -eq 124 ]; then
    exit 2
  fi
  exit "$code"
else
  echo "No GUI dialog tool (zenity/xmessage) available - failing safe as 'no'." >&2
  exit 1
fi
