---
name: say
description: Speaks a message aloud via the say script (spd-say), and with --notify also sends a desktop notification and a KDE Connect phone ping. Use when the user says "let me know" / "lemme know" (voice only), or "notify me" / "notify me when ..." (voice + notification + phone). Also use when asked to "say" something.
---

# Say Skill

Never run `spd-say`, `notify-send` or `kdeconnect-cli` directly. Always go through `run.sh`.

## When to use which

| User says | Command |
|---|---|
| "let me know ..." / "lemme know ..." | `run.sh "<message>"` (voice only) |
| "notify me ..." / "notify me when ..." | `run.sh --notify "<message>"` (voice + desktop + phone) |
| "say <thing>" | `run.sh "<thing>"` (interpret by intent, e.g. "say hello to me" speaks "hello") |

## Rules

- Write the full text answer first, then run the script once the response is complete.
  Don't run it during reasoning or while subagents are still working.
- Use a short, natural message that fits the situation (e.g. "All done, the tests pass"), not just "done".
- Run it in addition to the normal text reply, not instead of it.

## Usage

```bash
~/.pi/agent/skills/say/run.sh "I'm all done"
~/.pi/agent/skills/say/run.sh --notify "Task complete"
```

## What the script does

- Default: `spd-say "<text>"`
- `--notify` / `-n`: first `notify-send -u critical "Pi" "<text>"`, then
  `kdeconnect-cli -n "Galaxy S25 Ultra" --ping-msg "<text>"`, then speaks via `spd-say`.
- `--help` / `-h`: prints usage.
