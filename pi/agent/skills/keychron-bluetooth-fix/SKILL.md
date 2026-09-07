---
name: keychron-bluetooth-fix
description: Fixes Josh's Keychron K8 Pro keyboard when it won't pair/connect over Bluetooth on his laptop "alfie" (Linux Mint), including the classic connect/disconnect loop. Use whenever Josh says his keyboard/Keychron is disconnected, won't connect, is stuck in a loop, or asks to "fix the keyboard"/"fix my bluetooth keyboard".
---

# Keychron K8 Pro Bluetooth fix (laptop "alfie")

Josh's Keychron K8 Pro keyboard periodically loses its Bluetooth bond/pairing
and stops connecting on his Linux Mint laptop "alfie", even though it
normally works fine 99% of the time. When this happens, run the fix below
directly — don't ask for permission first, just do it and report back.

## Known device info

- Device name: `Keychron K8 Pro`
- MAC address: `6C:93:08:62:3D:65`
- Symptom: keyboard shows as paired/trusted but `Connected: no`, or
  pair/connect attempts fail with errors like `org.bluez.Error.Failed
  br-connection-create-socket` or `AuthenticationCanceled`, or it connects
  and then immediately disconnects again (classic connect/disconnect loop).

## Likely root cause(s)

Not 100% certain which of these is the actual trigger each time — could be
any combination:

1. **Bonding/encryption key desync (most likely)** — Bluetooth pairing uses a
   shared long-term key (LTK). If the host's Bluetooth stack restarts,
   resumes badly from suspend, or the adapter resets/crashes, the host can
   end up with stale keys while the keyboard still thinks it's bonded. This
   is why "remove the old pairing, then re-pair" reliably fixes it — it
   regenerates matching keys on both sides.
2. **Keyboard's multi-device profile switching** — the K8 Pro has 3 BT
   profile slots (Fn+1/2/3). Switching it to pair with another device (phone,
   tablet) and back can leave the slot's state slightly out of sync with the
   laptop's stored bond.
3. **Suspend/resume or Bluetooth firmware/driver reload** — can leave hci0 in
   a half-reset state where old bonds don't resume cleanly.
4. **L2CAP ERTM (Enhanced Retransmission Mode)** — occasionally implicated in
   `br-connection-create-socket` failures for this keyboard. Disabling it
   (`disable_ertm`) has coincided with a successful fix, but since the issue
   normally doesn't happen, ERTM is probably a contributing/intermittent
   factor rather than the sole cause. Not proven persistent/root-cause — an
   optional extra step, not the main fix.

## The fix — do these steps directly when asked to "fix" the keyboard

1. Check current state first:
   ```bash
   echo -e "info 6C:93:08:62:3D:65\nquit" | bluetoothctl
   ```
2. If it looks stuck (Connected: no, or repeated failures), wipe the stale
   pairing:
   ```bash
   bluetoothctl remove 6C:93:08:62:3D:65
   ```
3. Ask Josh to put the keyboard into pairing mode (hold `Fn+1` ~4 seconds
   until the light fast-blinks) if it isn't already.
4. Scan until it reappears:
   ```bash
   timeout 12 bluetoothctl --timeout 12 scan on
   echo -e "devices\nquit" | bluetoothctl | grep -i keychron
   ```
5. Pair, trust, connect:
   ```bash
   bluetoothctl pair 6C:93:08:62:3D:65
   bluetoothctl trust 6C:93:08:62:3D:65
   bluetoothctl connect 6C:93:08:62:3D:65
   ```
6. Tell Josh to type on it **immediately** after connect — it can idle-
   disconnect within ~30-60s of connecting if left untouched.
7. If `bluetoothctl` reports `power on` succeeded but `hciconfig -a` still
   shows the adapter DOWN or `rfkill list bluetooth` shows soft-blocked
   (this can happen after a `systemctl restart bluetooth`, e.g. if the ERTM
   toggle below was applied), run:
   ```bash
   rfkill unblock bluetooth
   echo -e "power on\nquit" | bluetoothctl
   ```
   This also lets Josh's other Bluetooth devices (Sony Headphones/Buds,
   MX Master 3S mouse) reconnect automatically.

## Optional extra step (only if the above alone doesn't work)

Disable L2CAP ERTM before retrying the pair/connect sequence above:
```bash
echo Y | sudo tee /sys/module/bluetooth/parameters/disable_ertm
sudo systemctl restart bluetooth
```
Note: this needs Josh's sudo password interactively, resets on reboot, and
restarting the bluetooth service can soft-block the adapter (see step 7
above to recover from that).

## Notes

- Don't bother with Blueman/GUI Bluetooth managers for this — use
  `bluetoothctl` directly, it's more reliable for this specific device.
- Don't overthink the root cause when fixing — just run the remove → pair →
  trust → connect sequence; that has reliably resolved it before.
