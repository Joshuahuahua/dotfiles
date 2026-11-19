#!/usr/bin/env bash
set -euo pipefail

show_usage() {
  cat <<EOF
Usage: $0 <message>
       $0 --notify "message"

Speaks message aloud using spd-say. With --notify, also sends system notification and pings phone.

Examples:
  $0 "I'm all done"
  $0 --notify "Task complete"
EOF
}

# Check for help flag first
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
  show_usage
  exit 0
fi

notified=false
text=""

# Parse arguments - check for notify flag first
if [[ "$1" == "--notify" || "$1" == "-n" ]]; then
  notified=true
  shift
fi

text="$1"

# Check if first arg was "notify" mode (not a flag)
if [[ "$text" == "notify" ]]; then
  notified=true
  text="$2"
fi

# Check we have text
if [[ -z "$text" ]]; then
  show_usage
  exit 1
fi

# If notify mode, send notifications first before speech
if [[ "$notified" == true ]]; then
  # Desktop notification (critical priority for reliability)
  notify-send -u critical "Pi" "$text"
  
  # Phone ping via kdeconnect
  kdeconnect-cli -n "Galaxy S25 Ultra" --ping-msg "$text"
fi

# Always speak via spd-say (after notifications in notify mode)
spd-say "$text"
