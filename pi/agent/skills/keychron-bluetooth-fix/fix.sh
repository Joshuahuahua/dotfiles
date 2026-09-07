#!/usr/bin/env bash
# Fix script for Josh's Keychron K8 Pro Bluetooth pairing issues on laptop "alfie".
# See SKILL.md in this directory for background/root-cause notes.
#
# Usage:
#   ./fix.sh            # normal fix: remove old pairing, re-pair, trust, connect
#   ./fix.sh --ertm      # also disable L2CAP ERTM first (needs sudo password)
#
# The keyboard must be put into pairing mode (Fn+1, hold ~4s) when prompted.

set -uo pipefail

MAC="6C:93:08:62:3D:65"
NAME="Keychron K8 Pro"

log() { echo ">> $*"; }

ensure_adapter_up() {
  if rfkill list bluetooth 2>/dev/null | grep -q "Soft blocked: yes"; then
    log "Adapter is soft-blocked, unblocking..."
    rfkill unblock bluetooth
    sleep 1
  fi
  if ! hciconfig 2>/dev/null | grep -q "UP RUNNING"; then
    log "Powering on adapter..."
    echo -e "power on\nquit" | bluetoothctl >/dev/null
    sleep 1
  fi
}

if [[ "${1:-}" == "--ertm" ]]; then
  log "Disabling L2CAP ERTM (requires sudo)..."
  echo Y | sudo tee /sys/module/bluetooth/parameters/disable_ertm >/dev/null
  sudo systemctl restart bluetooth
  sleep 2
  ensure_adapter_up
fi

ensure_adapter_up

log "Removing any stale pairing for $NAME ($MAC)..."
bluetoothctl remove "$MAC" >/dev/null 2>&1

echo
echo "Put the $NAME into pairing mode now (Fn+1, hold ~4s until it fast-blinks)."
read -rp "Press Enter once it's flashing... "

log "Scanning for $NAME (up to 15s)..."
timeout 15 bluetoothctl --timeout 15 scan on >/dev/null

if ! echo -e "devices\nquit" | bluetoothctl | grep -qi "$MAC"; then
  echo "!! Could not find $NAME during scan. Make sure it's in pairing mode and try again."
  exit 1
fi

log "Pairing..."
bluetoothctl pair "$MAC"

log "Trusting..."
bluetoothctl trust "$MAC"

log "Connecting..."
bluetoothctl connect "$MAC"

echo
echo "Done. Type on the keyboard NOW — it can idle-disconnect within ~30-60s if left untouched."

echo -e "info $MAC\nquit" | bluetoothctl
