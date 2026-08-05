---
name: toggl-track
description: Queries Josh's Toggl Track time entries using a read API token. Use whenever asked what he tracked/worked on/did "yesterday", "today", "on <date>", over a date range, or what's currently running in Toggl.
---

# Toggl Track

Query Josh's Toggl Track (time tracking) calendar/entries using the Toggl
Track API v9.

Use this skill whenever asked things like:
- "What did I do yesterday / today (in Toggl)?"
- "What was I tracking on <date>?"
- "What have I tracked this week / between X and Y?"
- "Is anything currently running in Toggl?"

## API reference

- Auth: HTTP Basic Auth, API token as username, literal string `api_token` as
  password. See
  https://engineering.toggl.com/docs/track/authentication/#http-basic-auth-with-api-token
- Time entries endpoint:
  https://engineering.toggl.com/docs/track/api/time_entries/#get-timeentries
  (`GET /me/time_entries?start_date=...&end_date=...`)
- Base URL: `https://api.track.toggl.com/api/v9`

## Authentication (API token)

The token is kept out of git history via the dotfiles repo's `.gitignore`:

- File: `~/.pi/agent/skills/toggl-track/.token` (resolves to
  `/home/josh/development/clones/dotfiles/pi/agent/skills/toggl-track/.token`,
  since `~/.pi/agent/skills` is symlinked into the dotfiles repo). The
  dotfiles repo's `.gitignore` excludes `pi/agent/skills/toggl-track/.token`
  — do not remove that entry.
- The helper script finds this file automatically next to itself. It also
  checks `TOGGL_API_TOKEN_FILE` (custom path) and `TOGGL_API_TOKEN` (inline
  env var) first.
- If the file still contains the placeholder `PASTE_YOUR_TOGGL_API_TOKEN_HERE`,
  the script fails with a clear error — tell Josh to paste his token in and
  re-run.
- Never print the token contents, never commit this file, never paste the
  token into chat.

## Helper script

Script: `scripts/toggl.py` (resolve relative to this SKILL.md's directory,
i.e. `/home/josh/.pi/agent/skills/toggl-track/scripts/toggl.py`). Run with
`python3`. No extra dependencies (stdlib only).

```bash
# Confirm auth / see whose account this is
python3 toggl.py whoami

# Today / yesterday
python3 toggl.py today
python3 toggl.py yesterday

# A specific date
python3 toggl.py on 2026-08-04

# A date range (inclusive both ends)
python3 toggl.py range 2026-08-01 2026-08-05

# What's running right now
python3 toggl.py running
```

`today`/`yesterday`/`on`/`range` print each time entry as:
```
HH:MM-HH:MM  duration  [Project Name] Description [tags]
```
sorted by start time, followed by a total tracked duration for the period.
Project names are resolved via `/me/projects` (cached per-invocation).

## Notes

- Dates are in the format `YYYY-MM-DD`.
- If a request is loosely worded ("what did I get up to Tuesday") work out
  the concrete date before calling `on`.
- If nothing was tracked in the period, the script prints
  `(no time entries)` — report that plainly rather than treating it as an
  error.
