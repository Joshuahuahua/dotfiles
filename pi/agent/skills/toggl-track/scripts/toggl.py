#!/usr/bin/env python3
"""
Thin Toggl Track REST API (v9) client used by the toggl-track pi skill.

Auth: HTTP Basic Auth with the API token as username and the literal string
"api_token" as password, per
https://engineering.toggl.com/docs/track/authentication/#http-basic-auth-with-api-token

Reads config from environment variables:
  TOGGL_API_TOKEN       Inline API token (takes priority over the token file)
  TOGGL_API_TOKEN_FILE  Path to a file containing the token (default: the
                        .token file stored alongside this script in the
                        toggl-track skill dir)

Usage:
  toggl.py whoami
  toggl.py today
  toggl.py yesterday
  toggl.py on <YYYY-MM-DD>
  toggl.py range <YYYY-MM-DD> <YYYY-MM-DD>
  toggl.py running
"""

import base64
import json
import os
import sys
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timedelta, date

API_BASE = "https://api.track.toggl.com/api/v9"


def find_token_file():
    candidates = []
    env_file = os.environ.get("TOGGL_API_TOKEN_FILE")
    if env_file:
        candidates.append(env_file)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidates.append(os.path.join(os.path.dirname(script_dir), ".token"))
    for path in candidates:
        if path and os.path.isfile(path):
            return path
    return None


def get_config():
    token = os.environ.get("TOGGL_API_TOKEN")
    if not token:
        token_file = find_token_file()
        if not token_file:
            sys.exit(
                "error: no Toggl API token found. Set TOGGL_API_TOKEN or create a .token file."
            )
        with open(token_file) as f:
            token = f.read().strip()
        if not token or token == "PASTE_YOUR_TOGGL_API_TOKEN_HERE":
            sys.exit(f"error: {token_file} has no real token in it yet.")
    return {"token": token}


def request(cfg, method, path, params=None):
    url = f"{API_BASE}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    auth = base64.b64encode(f"{cfg['token']}:api_token".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    req = urllib.request.Request(url, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            body = resp.read().decode()
            return json.loads(body) if body else None
    except urllib.error.HTTPError as e:
        detail = e.read().decode()
        sys.exit(f"error: {e.code} {e.reason} for {url}\n{detail}")


def get_project_map(cfg):
    projects = request(cfg, "GET", "/me/projects", {"include_archived": "true"}) or []
    return {p["id"]: p["name"] for p in projects}


def format_duration(seconds):
    if seconds < 0:
        return "running"
    h, rem = divmod(int(seconds), 3600)
    m, _ = divmod(rem, 60)
    return f"{h}h{m:02d}m" if h else f"{m}m"


def print_entries(entries, project_map):
    if not entries:
        print("(no time entries)")
        return

    total = 0
    for e in sorted(entries, key=lambda x: x.get("start", "")):
        duration = e.get("duration", 0)
        if duration >= 0:
            total += duration
        project_name = project_map.get(e.get("project_id"), "No Project")
        desc = e.get("description") or "(no description)"
        start = e.get("start", "")[11:16] if e.get("start") else "?"
        stop = e.get("stop", "")[11:16] if e.get("stop") else "running"
        tags = f" [{', '.join(e['tags'])}]" if e.get("tags") else ""
        print(f"{start}-{stop}  {format_duration(duration):>8}  [{project_name}] {desc}{tags}")

    print(f"\nTotal tracked: {format_duration(total)}")


def cmd_whoami(cfg, args):
    me = request(cfg, "GET", "/me")
    print(f"{me.get('fullname')} <{me.get('email')}> (timezone: {me.get('timezone')})")


def get_entries_for_range(cfg, start_date, end_date):
    return request(
        cfg,
        "GET",
        "/me/time_entries",
        {"start_date": start_date.isoformat(), "end_date": end_date.isoformat()},
    ) or []


def cmd_day(cfg, day):
    entries = get_entries_for_range(cfg, day, day + timedelta(days=1))
    project_map = get_project_map(cfg)
    print(f"--- Toggl entries for {day.isoformat()} ---")
    print_entries(entries, project_map)


def cmd_today(cfg, args):
    cmd_day(cfg, date.today())


def cmd_yesterday(cfg, args):
    cmd_day(cfg, date.today() - timedelta(days=1))


def cmd_on(cfg, args):
    day = datetime.strptime(args[0], "%Y-%m-%d").date()
    cmd_day(cfg, day)


def cmd_range(cfg, args):
    start = datetime.strptime(args[0], "%Y-%m-%d").date()
    end = datetime.strptime(args[1], "%Y-%m-%d").date()
    entries = get_entries_for_range(cfg, start, end + timedelta(days=1))
    project_map = get_project_map(cfg)
    print(f"--- Toggl entries from {start.isoformat()} to {end.isoformat()} ---")
    print_entries(entries, project_map)


def cmd_running(cfg, args):
    entry = request(cfg, "GET", "/me/time_entries/current")
    if not entry:
        print("(nothing currently running)")
        return
    project_map = get_project_map(cfg)
    project_name = project_map.get(entry.get("project_id"), "No Project")
    desc = entry.get("description") or "(no description)"
    started = entry.get("start", "")
    print(f"Running: [{project_name}] {desc} (started {started})")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1]
    args = sys.argv[2:]
    cfg = get_config()

    commands = {
        "whoami": cmd_whoami,
        "today": cmd_today,
        "yesterday": cmd_yesterday,
        "on": cmd_on,
        "range": cmd_range,
        "running": cmd_running,
    }

    handler = commands.get(cmd)
    if not handler:
        print(__doc__)
        sys.exit(1)
    handler(cfg, args)


if __name__ == "__main__":
    main()
