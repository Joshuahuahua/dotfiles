---
name: say
description: Speaks text aloud using spd-say, optionally also sending system notification and kdeconnect alert to phone. Use when user asks you to 'say' something or make them aware via voice/audio feedback.
metadata:
  requires-confirmation: false
---
# Say Skill

## Description

Speak text aloud using the `spd-say` command (text-to-speech). Optionally, also send a system notification and ping the user's phone via kdeconnect when the `--notify` flag is passed.

## Usage

```bash
pi say <text to speak>
pi say --notify "your message"  # Also triggers desktop notification + phone alert
```

When invoked without arguments or with `--help`, displays usage instructions.

## Behavior

### Default (voice only)
- Triggers: `spd-say "<text>"`
- Result: Text is spoken aloud via system TTS

### With --notify flag (voice + notification + phone ping)
1. Spoken aloud: `spd-say "<text>"`
2. Desktop alert: `notify-send -u critical "Pi" "<text>"`
3. Phone ping: `kdeconnect-cli -n "Galaxy S25 Ultra" --ping-msg "<text>"`

## Examples

```bash
pi say "I'm all done"
# Spoken aloud

pi say --notify "Task complete"
# Spoken aloud + desktop notification + phone alert
```

## Parameters

- `<text>`: The message to speak (required unless --help/--notify without argument)
- `--notify`: Optional flag to also trigger system notification and phone ping

---

*Uses spd-say for speech, notify-send for desktop alerts, kdeconnect-cli for phone notifications.*
