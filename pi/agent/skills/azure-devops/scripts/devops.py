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
  devops.py open [<repo> <pr-id>] [--path DIR]   # open a PR's web URL in the browser (defaults to current git branch's PR)

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


def is_me(cfg, identity):
    """True if an Azure DevOps identity object (createdBy/author/etc.) refers
    to the configured user, matching on email (uniqueName) or display name."""
    if not identity:
        return False
    unique_name = (identity.get("uniqueName") or "").lower()
    display_name = (identity.get("displayName") or "").lower()
    me = cfg["me"].lower()
    return unique_name == me or display_name == me.split("@")[0].replace(".", " ")


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


def request(cfg, method, url, body=None, content_type="application/json"):
    token = base64.b64encode(f":{cfg['pat']}".encode()).decode()
    headers = {
        "Authorization": f"Basic {token}",
        "Content-Type": content_type,
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


def cmd_workitem_delete(cfg, args):
    """Delete a work item.

    Usage: workitem-delete <id>

    Always a soft-delete: the item moves to the project's recycle bin and
    remains recoverable there. Permanent destruction is intentionally not
    supported by this command - there is no flag or code path that can
    pass destroy=true to the API, by design.
    """
    if not args:
        sys.exit("usage: workitem-delete <id>")

    wi_id = args[0]

    url = project_url(cfg, f"_apis/wit/workitems/{wi_id}?api-version={API_VERSION}")
    request(cfg, "DELETE", url)
    print(f"Deleted #{wi_id} (moved to recycle bin)")


def cmd_workitem_create(cfg, args):
    """Create a work item.

    Usage: workitem-create <type> <title> [--description TEXT]
           [--assigned-to EMAIL] [--iteration PATH] [--area PATH]
           [--parent ID] [--tags "a; b"] [--estimate HOURS]

    <type> is a work item type name, e.g. Task, Bug, "User Story".
    """
    if len(args) < 2:
        sys.exit("usage: workitem-create <type> <title> [--description TEXT] "
                  "[--assigned-to EMAIL] [--iteration PATH] [--area PATH] "
                  "[--parent ID] [--tags \"a; b\"] [--estimate HOURS]")

    wi_type, title = args[0], args[1]
    rest = args[2:]
    opts = {}
    i = 0
    while i < len(rest):
        if rest[i].startswith("--") and i + 1 < len(rest):
            opts[rest[i][2:]] = rest[i + 1]
            i += 2
        else:
            i += 1

    patch = [{"op": "add", "path": "/fields/System.Title", "value": title}]
    if "description" in opts:
        # The "Bug" work item type uses Repro Steps as its required narrative field
        # instead of (plain) Description - Azure DevOps rejects a Bug with Description
        # set but Repro Steps empty.
        description_field = (
            "Microsoft.VSTS.TCM.ReproSteps" if wi_type.lower() == "bug" else "System.Description"
        )
        patch.append({"op": "add", "path": f"/fields/{description_field}", "value": opts["description"]})
    if "assigned-to" in opts:
        patch.append({"op": "add", "path": "/fields/System.AssignedTo", "value": opts["assigned-to"]})
    if "iteration" in opts:
        patch.append({"op": "add", "path": "/fields/System.IterationPath", "value": opts["iteration"]})
    if "area" in opts:
        patch.append({"op": "add", "path": "/fields/System.AreaPath", "value": opts["area"]})
    if "tags" in opts:
        patch.append({"op": "add", "path": "/fields/System.Tags", "value": opts["tags"]})
    if "estimate" in opts:
        patch.append({"op": "add", "path": "/fields/Microsoft.VSTS.Scheduling.OriginalEstimate", "value": opts["estimate"]})
    if "parent" in opts:
        patch.append({
            "op": "add",
            "path": "/relations/-",
            "value": {
                "rel": "System.LinkTypes.Hierarchy-Reverse",
                "url": org_url(cfg, f"_apis/wit/workItems/{opts['parent']}"),
            },
        })

    type_segment = urllib.parse.quote(f"${wi_type}")
    url = project_url(cfg, f"_apis/wit/workitems/{type_segment}?api-version={API_VERSION}")
    result = request(cfg, "POST", url, patch, content_type="application/json-patch+json")
    wi_id = result.get("id")
    wi_url = org_url(cfg, f"{cfg['project']}/_workitems/edit/{wi_id}") if wi_id else None
    print(f"Created #{wi_id} [{wi_type}] {title}")
    if wi_url:
        print(wi_url)


def cmd_workitem_update(cfg, args):
    """Update fields on an existing work item.

    Usage: workitem-update <id> [--state STATE] [--title TEXT]
           [--description TEXT] [--assigned-to EMAIL] [--iteration PATH]
           [--area PATH] [--tags "a; b"]

    At least one field option must be given. Only the fields passed are
    changed - everything else on the work item is left as-is.
    """
    if len(args) < 1:
        sys.exit("usage: workitem-update <id> [--state STATE] [--title TEXT] "
                  "[--description TEXT] [--assigned-to EMAIL] [--iteration PATH] "
                  "[--area PATH] [--tags \"a; b\"]")

    wi_id = args[0]
    rest = args[1:]
    opts = {}
    i = 0
    while i < len(rest):
        if rest[i].startswith("--") and i + 1 < len(rest):
            opts[rest[i][2:]] = rest[i + 1]
            i += 2
        else:
            i += 1

    field_map = {
        "state": "System.State",
        "title": "System.Title",
        "description": "System.Description",
        "assigned-to": "System.AssignedTo",
        "iteration": "System.IterationPath",
        "area": "System.AreaPath",
        "tags": "System.Tags",
    }

    patch = [
        {"op": "add", "path": f"/fields/{field_map[key]}", "value": value}
        for key, value in opts.items()
        if key in field_map
    ]
    if not patch:
        sys.exit("error: no recognised field options given - nothing to update")

    url = project_url(cfg, f"_apis/wit/workitems/{wi_id}?api-version={API_VERSION}")
    result = request(cfg, "PATCH", url, patch, content_type="application/json-patch+json")
    fields = result.get("fields", {})
    print(f"Updated #{wi_id} [{fields.get('System.WorkItemType')}] {fields.get('System.Title')}")
    for key in opts:
        if key in field_map:
            print(f"  {field_map[key]} -> {fields.get(field_map[key])}")


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
    # Note: searchCriteria.creatorId requires a GUID identity, not an email,
    # so "mine" filtering is done client-side below instead of via the API.
    if source_branch:
        ref = source_branch if source_branch.startswith("refs/heads/") else f"refs/heads/{source_branch}"
        params["searchCriteria.sourceRefName"] = ref

    url = project_url(cfg, path) + "?" + urllib.parse.urlencode(params)
    result = request(cfg, "GET", url)
    prs = result.get("value", [])
    if mine:
        prs = [pr for pr in prs if is_me(cfg, pr.get("createdBy", {}))]
    for pr in prs:
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
        print(f"  Link: {pr_web_url(cfg, repo, pr_id)}?discussionId={thread['id']}")
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


def pr_web_url(cfg, repo, pr_id):
    org = urllib.parse.quote(cfg["org"])
    project = urllib.parse.quote(cfg["project"])
    repo_q = urllib.parse.quote(repo)
    return f"https://dev.azure.com/{org}/{project}/_git/{repo_q}/pullrequest/{pr_id}"


def cmd_open(cfg, args):
    """Open a PR's web URL in the default browser. If no repo/pr-id is given,
    detect the current git branch and open the matching open/draft PR."""
    path = os.getcwd()
    if "--path" in args:
        idx = args.index("--path")
        path = args[idx + 1]
        args = args[:idx] + args[idx + 2 :]

    positional = [a for a in args if not a.startswith("--")]

    if len(positional) >= 2:
        repo, pr_id = positional[0], positional[1]
    else:
        branch = detect_git_branch(path)
        if not branch or branch == "HEAD":
            sys.exit(f"error: could not determine a git branch in {path}")
        pr = find_pr_for_branch(cfg, branch)
        if not pr:
            print(f"No open/draft PR found with source branch '{branch}'.")
            return
        repo, pr_id = pr["repository"]["name"], pr["pullRequestId"]

    url = pr_web_url(cfg, repo, pr_id)
    print(url)
    try:
        subprocess.run(["xdg-open", url], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"(could not launch browser automatically: {e})")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1]
    args = sys.argv[2:]
    cfg = get_config()

    commands = {
        "workitem": cmd_workitem,
        "workitem-create": cmd_workitem_create,
        "workitem-update": cmd_workitem_update,
        "workitem-delete": cmd_workitem_delete,
        "query": cmd_query,
        "my-active": cmd_my_active,
        "sprint": cmd_sprint,
        "prs": cmd_prs,
        "pr": cmd_pr,
        "pr-comments": cmd_pr_comments,
        "here": cmd_here,
        "open": cmd_open,
    }

    handler = commands.get(cmd)
    if not handler:
        print(__doc__)
        sys.exit(1)
    handler(cfg, args)


if __name__ == "__main__":
    main()
