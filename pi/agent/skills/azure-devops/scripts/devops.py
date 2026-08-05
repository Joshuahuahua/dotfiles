#!/usr/bin/env python3
"""
Thin Azure DevOps REST API client used by the azure-devops pi skill.

Reads config from environment variables (with sensible defaults for this
user's setup):
  AZDO_ORG       Azure DevOps organization name (default: diversus)
  AZDO_PROJECT   Azure DevOps project name (default: "Huddler - Product")
  AZDO_PAT_FILE  Path to a file containing the PAT (default: the .pat file
                 stored alongside this script in the azure-devops skill dir)
  AZDO_ME        Email used for "assigned to me" queries
                 (default: joshua.hollander@diversus.com.au)

Usage:
  devops.py workitem <id>
  devops.py query "<WIQL WHERE clause>" [--top N] [--all-types] [--all-sprints]
  devops.py my-active [--top N] [--all-types] [--all-sprints]
  devops.py sprint [--top N] [--all-types]
  devops.py prs [--repo NAME] [--status active|completed|abandoned|all] [--mine] [--source-branch NAME]
  devops.py pr-comments <repo> <pr-id>
  devops.py pr <repo> <pr-id>
  devops.py here [--path DIR]            # find PR for current git branch + show unresolved comments

Default scope (rule of thumb, unless told otherwise):
  - Only the current sprint (@CurrentIteration) for `query` and `my-active`
    (use --all-sprints to remove this restriction). `sprint` is always
    current-sprint by definition.
  - Only these work item types: Task, Activity, Sub Activity, Bug, Hotfix
    (use --all-types to remove this restriction).
"""

import base64
import json
import os
import subprocess
import sys
import urllib.request
import urllib.parse
import urllib.error

API_VERSION = "7.1"

# Default work item type scope: unless told otherwise, only these types are
# relevant (excludes User Stories, Features, Epics, etc.)
DEFAULT_TYPES = ["Task", "Activity", "Sub Activity", "Bug", "Hotfix"]


def type_filter_clause(types=None):
    types = types or DEFAULT_TYPES
    quoted = ", ".join(f"'{t}'" for t in types)
    return f"[System.WorkItemType] IN ({quoted})"


def find_pat_file():
    candidates = []
    env_file = os.environ.get("AZDO_PAT_FILE")
    if env_file:
        candidates.append(env_file)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidates.append(os.path.join(os.path.dirname(script_dir), ".pat"))
    candidates.append(os.path.join(os.getcwd(), ".azure-devops-pat"))
    for path in candidates:
        if path and os.path.isfile(path):
            return path
    return None


def get_config():
    org = os.environ.get("AZDO_ORG", "diversus")
    project = os.environ.get("AZDO_PROJECT", "Huddler - Product")
    me = os.environ.get("AZDO_ME", "joshua.hollander@diversus.com.au")

    pat = os.environ.get("AZDO_PAT")
    if not pat:
        pat_file = find_pat_file()
        if not pat_file:
            sys.exit(
                "error: no PAT found. Set AZDO_PAT or create a .azure-devops-pat file."
            )
        with open(pat_file) as f:
            pat = f.read().strip()
        if not pat or pat == "PASTE_YOUR_PAT_HERE":
            sys.exit(f"error: {pat_file} has no real token in it yet.")

    return {"org": org, "project": project, "me": me, "pat": pat}


def request(cfg, method, url, body=None):
    token = base64.b64encode(f":{cfg['pat']}".encode()).decode()
    headers = {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        detail = e.read().decode()
        sys.exit(f"error: {e.code} {e.reason} for {url}\n{detail}")


def org_url(cfg, path):
    return f"https://dev.azure.com/{urllib.parse.quote(cfg['org'])}/{path}"


def project_url(cfg, path):
    return org_url(cfg, f"{urllib.parse.quote(cfg['project'])}/{path}")


def cmd_workitem(cfg, args):
    wi_id = args[0]
    url = project_url(
        cfg, f"_apis/wit/workitems/{wi_id}?$expand=all&api-version={API_VERSION}"
    )
    print(json.dumps(request(cfg, "GET", url), indent=2))


def run_wiql(cfg, where_clause, top=50):
    query = (
        "SELECT [System.Id], [System.Title], [System.State], [System.WorkItemType], "
        "[System.AssignedTo], [System.IterationPath] FROM WorkItems WHERE "
        f"{where_clause} ORDER BY [System.ChangedDate] DESC"
    )
    url = project_url(cfg, f"_apis/wit/wiql?api-version={API_VERSION}")
    result = request(cfg, "POST", url, {"query": query})
    ids = [str(r["id"]) for r in result.get("workItems", [])][:top]
    if not ids:
        return []
    batch_url = org_url(cfg, f"_apis/wit/workitemsbatch?api-version={API_VERSION}")
    fields = [
        "System.Id",
        "System.Title",
        "System.State",
        "System.WorkItemType",
        "System.AssignedTo",
        "System.IterationPath",
    ]
    batch = request(
        cfg, "POST", batch_url, {"ids": [int(i) for i in ids], "fields": fields}
    )
    return batch.get("value", [])


def print_workitems(items):
    for wi in items:
        f = wi["fields"]
        assigned = f.get("System.AssignedTo", {})
        assigned_name = assigned.get("displayName") if isinstance(assigned, dict) else assigned
        print(
            f"#{wi['id']} [{f.get('System.WorkItemType')}] {f.get('System.State')} - "
            f"{f.get('System.Title')} (assigned: {assigned_name}, iteration: {f.get('System.IterationPath')})"
        )


def cmd_sprint(cfg, args):
    top = 50
    all_types = "--all-types" in args
    if "--top" in args:
        top = int(args[args.index("--top") + 1])
    where = (
        f"[System.TeamProject] = '{cfg['project']}' AND "
        "[System.IterationPath] = @CurrentIteration"
    )
    if not all_types:
        where += f" AND {type_filter_clause()}"
    print_workitems(run_wiql(cfg, where, top))


def cmd_query(cfg, args):
    top = 50
    all_types = "--all-types" in args
    all_sprints = "--all-sprints" in args
    where_parts = []
    i = 0
    while i < len(args):
        if args[i] == "--top":
            top = int(args[i + 1])
            i += 2
        elif args[i] in ("--all-types", "--all-sprints"):
            i += 1
        else:
            where_parts.append(args[i])
            i += 1
    where_clause = " ".join(where_parts)

    clauses = [where_clause] if where_clause else []
    if not all_sprints:
        clauses.append("[System.IterationPath] = @CurrentIteration")
    if not all_types:
        clauses.append(type_filter_clause())
    full_where = " AND ".join(f"({c})" for c in clauses)

    items = run_wiql(cfg, full_where, top)
    print_workitems(items)


def cmd_my_active(cfg, args):
    top = 50
    all_types = "--all-types" in args
    all_sprints = "--all-sprints" in args
    if "--top" in args:
        top = int(args[args.index("--top") + 1])
    where = (
        f"[System.TeamProject] = '{cfg['project']}' AND "
        f"[System.AssignedTo] = '{cfg['me']}' AND [System.State] = 'Active'"
    )
    if not all_sprints:
        where += " AND [System.IterationPath] = @CurrentIteration"
    if not all_types:
        where += f" AND {type_filter_clause()}"
    print_workitems(run_wiql(cfg, where, top))


def cmd_prs(cfg, args):
    repo = None
    status = "active"
    mine = False
    source_branch = None
    i = 0
    while i < len(args):
        if args[i] == "--repo":
            repo = args[i + 1]
            i += 2
        elif args[i] == "--status":
            status = args[i + 1]
            i += 2
        elif args[i] == "--mine":
            mine = True
            i += 1
        elif args[i] == "--source-branch":
            source_branch = args[i + 1]
            i += 2
        else:
            i += 1

    if repo:
        path = f"_apis/git/repositories/{urllib.parse.quote(repo)}/pullrequests"
    else:
        path = "_apis/git/pullrequests"

    params = {"api-version": API_VERSION}
    # Azure DevOps expects status=all to see across all statuses; if the user
    # asked for a source branch, default to "all" unless they gave --status.
    effective_status = status
    if source_branch and "--status" not in args:
        effective_status = "all"
    if effective_status != "all":
        params["searchCriteria.status"] = effective_status
    if mine:
        params["searchCriteria.creatorId"] = cfg["me"]
    if source_branch:
        ref = source_branch if source_branch.startswith("refs/heads/") else f"refs/heads/{source_branch}"
        params["searchCriteria.sourceRefName"] = ref

    url = project_url(cfg, path) + "?" + urllib.parse.urlencode(params)
    result = request(cfg, "GET", url)
    for pr in result.get("value", []):
        print(
            f"#{pr['pullRequestId']} [{pr['status']}] {pr['title']} "
            f"({pr['repository']['name']}, by {pr['createdBy']['displayName']}, branch: {pr['sourceRefName']})"
        )


def cmd_pr(cfg, args):
    repo, pr_id = args[0], args[1]
    url = project_url(
        cfg,
        f"_apis/git/repositories/{urllib.parse.quote(repo)}/pullrequests/{pr_id}?api-version={API_VERSION}",
    )
    print(json.dumps(request(cfg, "GET", url), indent=2))


def cmd_pr_comments(cfg, args):
    repo, pr_id = args[0], args[1]
    print_pr_threads(cfg, repo, pr_id, unresolved_only=False)


RESOLVED_THREAD_STATUSES = {"fixed", "closed", "wontfix", "bydesign"}


def print_pr_threads(cfg, repo, pr_id, unresolved_only=False):
    url = project_url(
        cfg,
        f"_apis/git/repositories/{urllib.parse.quote(repo)}/pullRequests/{pr_id}/threads?api-version={API_VERSION}",
    )
    result = request(cfg, "GET", url)
    printed = 0
    for thread in result.get("value", []):
        comments = [c for c in thread.get("comments", []) if c.get("commentType") != "system"]
        if not comments:
            continue
        status = thread.get("status", "active")
        if unresolved_only and status.lower() in RESOLVED_THREAD_STATUSES:
            continue
        printed += 1
        print(f"--- Thread {thread['id']} (status: {status}) ---")
        for c in comments:
            author = c.get("author", {}).get("displayName", "unknown")
            print(f"  {author}: {c.get('content', '').strip()}")
    if printed == 0:
        print("(no unresolved comment threads)" if unresolved_only else "(no comment threads)")


def detect_git_branch(path):
    try:
        out = subprocess.run(
            ["git", "-C", path, "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return out.stdout.strip()
    except Exception:
        return None


def find_pr_for_branch(cfg, branch, repo=None):
    ref = branch if branch.startswith("refs/heads/") else f"refs/heads/{branch}"
    if repo:
        path = f"_apis/git/repositories/{urllib.parse.quote(repo)}/pullrequests"
    else:
        path = "_apis/git/pullrequests"
    params = {
        "api-version": API_VERSION,
        "searchCriteria.status": "active",
        "searchCriteria.sourceRefName": ref,
    }
    url = project_url(cfg, path) + "?" + urllib.parse.urlencode(params)
    result = request(cfg, "GET", url)
    prs = result.get("value", [])
    return prs[0] if prs else None


def cmd_here(cfg, args):
    """Find the open/draft PR for the current git branch and show its
    unresolved (non-system, non-fixed/closed) comment threads."""
    path = os.getcwd()
    if "--path" in args:
        path = args[args.index("--path") + 1]

    branch = detect_git_branch(path)
    if not branch or branch == "HEAD":
        sys.exit(f"error: could not determine a git branch in {path}")

    pr = find_pr_for_branch(cfg, branch)
    if not pr:
        print(f"No open/draft PR found with source branch '{branch}'.")
        return

    draft = " (draft)" if pr.get("isDraft") else ""
    print(
        f"PR #{pr['pullRequestId']}{draft} [{pr['status']}] {pr['title']} "
        f"({pr['repository']['name']}, branch: {branch})"
    )
    print()
    print_pr_threads(cfg, pr["repository"]["name"], pr["pullRequestId"], unresolved_only=True)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1]
    args = sys.argv[2:]
    cfg = get_config()

    commands = {
        "workitem": cmd_workitem,
        "query": cmd_query,
        "my-active": cmd_my_active,
        "sprint": cmd_sprint,
        "prs": cmd_prs,
        "pr": cmd_pr,
        "pr-comments": cmd_pr_comments,
        "here": cmd_here,
    }

    handler = commands.get(cmd)
    if not handler:
        print(__doc__)
        sys.exit(1)
    handler(cfg, args)


if __name__ == "__main__":
    main()
