#!/usr/bin/env bash
set -euo pipefail

show_usage() {
  cat <<EOF
Usage: $0 [--notify|-n] <message>

Speaks message aloud using spd-say.
With --notify, also sends a desktop notification and pings the phone via KDE Connect.

Examples:
  $0 "I'm all done"
  $0 --notify "Task complete"
EOF
}

notify=false

case "${1:-}" in
  --help|-h) show_usage; exit 0 ;;
  --notify|-n) notify=true; shift ;;
esac

text="${*:-}"

if [[ -z "$text" ]]; then
  show_usage
  exit 1
fi

if [[ "$notify" == true ]]; then
  notify-send -u critical "Pi" "$text" || true
  kdeconnect-cli -n "Galaxy S25 Ultra" --ping-msg "$text" || true
fi

spd-say "$text"
