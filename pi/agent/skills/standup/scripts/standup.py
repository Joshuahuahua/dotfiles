#!/usr/bin/env python3
"""
Fetches raw material for a "standup" docket (Yesterday / Today / Blocked)
from Toggl Track + Azure DevOps, and prints it via the devops-printer CLI.

This script deliberately does NOT try to rewrite/clean up the wording of
Toggl entries or PR/ticket titles — that's the AI's job. The intended
workflow is:

  1. `standup.py dump`            -> prints the raw data (plain, readable)
  2. the AI reads that and composes its own natural-English description text
  3. `standup.py print [flags]`   -> reads the final description from stdin
                                      and sends it to the devops-printer

Reuses the sibling azure-devops and toggl-track skill scripts directly
(imported by path) rather than re-implementing their API clients.

Usage:
  standup.py dump
  standup.py print [--preview] [--detailed] [--title TITLE] [--heading HEADING]
                    (reads description text from stdin)

--preview forwards straight through to the devops-printer `note` command
(prints to stdout instead of the physical printer). Always use this while
testing / previewing.
"""

import os
import re
import subprocess
import sys
from datetime import date, timedelta
from importlib import util as import_util

SKILLS_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
AZDO_SCRIPT = os.path.join(SKILLS_DIR, "azure-devops", "scripts", "devops.py")
TOGGL_SCRIPT = os.path.join(SKILLS_DIR, "toggl-track", "scripts", "toggl.py")
PRINTER_DIR = "/home/josh/development/personal/devopsPrinter"

ME_NAME = "Joshua Hollander"


def load_module(name, path):
    spec = import_util.spec_from_file_location(name, path)
    module = import_util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


devops = load_module("devops_mod", AZDO_SCRIPT)
toggl = load_module("toggl_mod", TOGGL_SCRIPT)


def tidy_whitespace(text):
    return re.sub(r"\s+", " ", text.strip())


def get_yesterday_entries():
    """Raw (deduplicated) Toggl entry descriptions for yesterday, with only
    whitespace tidied up -- no rewriting."""
    cfg = toggl.get_config()
    day = date.today() - timedelta(days=1)
    entries = toggl.get_entries_for_range(cfg, day, day + timedelta(days=1))
    seen = []
    for e in sorted(entries, key=lambda x: x.get("start", "")):
        desc = tidy_whitespace(e.get("description") or "(no description)")
        if desc not in seen:
            seen.append(desc)
    return seen


def get_active_tickets_today():
    cfg = devops.get_config()
    where = (
        f"[System.TeamProject] = '{cfg['project']}' AND "
        f"[System.AssignedTo] = '{cfg['me']}' AND [System.State] = 'Active' AND "
        f"[System.IterationPath] = @CurrentIteration AND {devops.type_filter_clause()}"
    )
    items = devops.run_wiql(cfg, where, 50)
    return [
        {
            "id": wi["id"],
            "title": wi["fields"].get("System.Title"),
            "type": wi["fields"].get("System.WorkItemType"),
        }
        for wi in items
    ]


def get_blocked_tickets():
    cfg = devops.get_config()
    where = (
        f"[System.TeamProject] = '{cfg['project']}' AND "
        f"[System.AssignedTo] = '{cfg['me']}' AND [System.State] = 'Blocked' AND "
        f"[System.IterationPath] = @CurrentIteration AND {devops.type_filter_clause()}"
    )
    items = devops.run_wiql(cfg, where, 50)
    return [
        {"id": wi["id"], "title": wi["fields"].get("System.Title")}
        for wi in items
    ]


def get_my_open_prs():
    cfg = devops.get_config()
    params = {
        "api-version": devops.API_VERSION,
        "searchCriteria.status": "active",
    }
    import urllib.parse

    url = devops.project_url(cfg, "_apis/git/pullrequests") + "?" + urllib.parse.urlencode(params)
    result = devops.request(cfg, "GET", url)
    prs = result.get("value", [])
    prs = [pr for pr in prs if not pr.get("isDraft")]
    return [pr for pr in prs if devops.is_me(cfg, pr.get("createdBy", {}))]


def get_prs_needing_response(prs):
    cfg = devops.get_config()
    needing_response = []
    for pr in prs:
        repo = pr["repository"]["name"]
        pr_id = pr["pullRequestId"]
        url = devops.project_url(
            cfg,
            f"_apis/git/repositories/{devops.urllib.parse.quote(repo)}/pullRequests/{pr_id}/threads?api-version={devops.API_VERSION}",
        )
        result = devops.request(cfg, "GET", url)
        for thread in result.get("value", []):
            comments = [c for c in thread.get("comments", []) if c.get("commentType") != "system"]
            if not comments:
                continue
            status = thread.get("status", "active")
            if status.lower() in devops.RESOLVED_THREAD_STATUSES:
                continue
            last_author = comments[-1].get("author", {}).get("displayName", "")
            if last_author == ME_NAME:
                continue
            first_comment = comments[0].get("content", "").strip()
            needing_response.append(
                {
                    "pr_id": pr_id,
                    "pr_title": pr["title"],
                    "thread_id": thread["id"],
                    "last_author": last_author,
                    "comment_preview": first_comment[:200],
                }
            )
    return needing_response


def get_prs_no_action_needed(prs, needs_response):
    """PRs of mine that don't need my input right now: either they have no
    unresolved comment threads at all, or every unresolved thread's last
    reply was already from me."""
    needs_action_ids = {r["pr_id"] for r in needs_response}
    return [pr for pr in prs if pr["pullRequestId"] not in needs_action_ids]


def get_all_active_prs(cfg):
    params = {
        "api-version": devops.API_VERSION,
        "searchCriteria.status": "active",
    }
    import urllib.parse

    url = devops.project_url(cfg, "_apis/git/pullrequests") + "?" + urllib.parse.urlencode(params)
    result = devops.request(cfg, "GET", url)
    return [pr for pr in result.get("value", []) if not pr.get("isDraft")]


def get_reviewer_prs_needing_attention(all_prs):
    """PRs NOT created by me, where I'm a reviewer, and I either haven't
    voted yet (vote == 0) or there's an unresolved comment thread whose last
    reply isn't mine."""
    cfg = devops.get_config()
    attention = []
    for pr in all_prs:
        if devops.is_me(cfg, pr.get("createdBy", {})):
            continue
        my_reviewer_entry = next(
            (r for r in pr.get("reviewers", []) if devops.is_me(cfg, r)), None
        )
        if my_reviewer_entry is None:
            continue

        reasons = []
        if my_reviewer_entry.get("vote", 0) == 0:
            reasons.append("haven't reviewed/voted yet")

        repo = pr["repository"]["name"]
        pr_id = pr["pullRequestId"]
        url = devops.project_url(
            cfg,
            f"_apis/git/repositories/{devops.urllib.parse.quote(repo)}/pullRequests/{pr_id}/threads?api-version={devops.API_VERSION}",
        )
        result = devops.request(cfg, "GET", url)
        reply_threads = []
        for thread in result.get("value", []):
            comments = [c for c in thread.get("comments", []) if c.get("commentType") != "system"]
            if not comments:
                continue
            status = thread.get("status", "active")
            if status.lower() in devops.RESOLVED_THREAD_STATUSES:
                continue
            last_author = comments[-1].get("author", {}).get("displayName", "")
            if last_author == ME_NAME:
                continue
            first_comment = comments[0].get("content", "").strip()
            reply_threads.append(
                {
                    "thread_id": thread["id"],
                    "last_author": last_author,
                    "comment_preview": first_comment[:200],
                }
            )

        if reply_threads or reasons:
            attention.append(
                {
                    "pr_id": pr_id,
                    "pr_title": pr["title"],
                    "author": pr["createdBy"]["displayName"],
                    "reasons": reasons,
                    "reply_threads": reply_threads,
                }
            )
    return attention


def cmd_dump(args):
    """Print raw data for all three sections, for the AI to read and turn
    into a naturally-worded description before calling `print`."""
    yesterday = get_yesterday_entries()
    active_tickets = get_active_tickets_today()
    my_prs = get_my_open_prs()
    needs_response = get_prs_needing_response(my_prs)
    no_action_prs = get_prs_no_action_needed(my_prs, needs_response)
    cfg = devops.get_config()
    all_active_prs = get_all_active_prs(cfg)
    reviewer_attention = get_reviewer_prs_needing_attention(all_active_prs)
    blocked = get_blocked_tickets()

    print("=== YESTERDAY (raw Toggl entry descriptions) ===")
    if yesterday:
        for e in yesterday:
            print(f"- {e}")
    else:
        print("(nothing tracked)")

    print("\n=== TODAY: active tickets this sprint ===")
    if active_tickets:
        for t in active_tickets:
            print(f"#{t['id']} [{t['type']}]: {t['title']}")
    else:
        print("(none)")

    print("\n=== TODAY: my open PRs ===")
    if my_prs:
        for pr in my_prs:
            print(f"PR #{pr['pullRequestId']} ({pr['repository']['name']}): {pr['title']}")
    else:
        print("(none)")

    print("\n=== TODAY: PR comment threads needing my reply (my own PRs) ===")
    if needs_response:
        for r in needs_response:
            print(
                f"PR #{r['pr_id']} ({r['pr_title']}) thread {r['thread_id']} "
                f"- last reply by {r['last_author']}: \"{r['comment_preview']}\""
            )
    else:
        print("(none)")

    print("\n=== TODAY: PRs I'm reviewing (not mine) needing my attention ===")
    print("(not voted yet, and/or unresolved comment thread I haven't replied to)")
    if reviewer_attention:
        for r in reviewer_attention:
            reason_bits = list(r["reasons"])
            for t in r["reply_threads"]:
                reason_bits.append(
                    f'thread {t["thread_id"]} - last reply by {t["last_author"]}: "{t["comment_preview"]}"'
                )
            print(f"PR #{r['pr_id']} ({r['pr_title']}, by {r['author']}): {'; '.join(reason_bits)}")
    else:
        print("(none)")

    print("\n=== ACTIVE PRS: my open PRs that do NOT need my input ===")
    print("(no unresolved comment threads, or I already replied last)")
    if no_action_prs:
        for pr in no_action_prs:
            print(f"PR #{pr['pullRequestId']} ({pr['repository']['name']}): {pr['title']}")
    else:
        print("(none)")

    print("\n=== BLOCKED: blocked tickets this sprint ===")
    if blocked:
        for t in blocked:
            print(f"#{t['id']}: {t['title']}")
    else:
        print("(none)")


def cmd_print(args):
    """Read the final (AI-composed) description text from stdin and send it
    to the devops-printer `note` command."""
    preview = "--preview" in args
    detailed = "--detailed" in args
    title = "Standup"
    heading = "STANDUP"
    if "--title" in args:
        title = args[args.index("--title") + 1]
    if "--heading" in args:
        heading = args[args.index("--heading") + 1]

    description = sys.stdin.read().strip()
    if not description:
        sys.exit("error: no description text provided on stdin")

    today_str = date.today().strftime("%d %b %Y")

    cmd = [
        "pnpm",
        "devops",
        "note",
        "--heading",
        heading,
        "--title",
        title,
        "--subtitle",
        today_str,
        "--description",
        description,
    ]
    if detailed:
        cmd.append("--detailed")
    if preview:
        cmd.append("--preview")

    result = subprocess.run(cmd, cwd=PRINTER_DIR)
    sys.exit(result.returncode)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1]
    args = sys.argv[2:]

    if cmd == "dump":
        cmd_dump(args)
    elif cmd == "print":
        cmd_print(args)
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
