#!/usr/bin/env python3
"""
Minimal Azure DevOps REST client for liking/unliking pull request comments.

This is deliberately narrow - it does nothing except list comment ids (to
pick a target) and add/remove/list likes on one comment. It reuses the same
PAT file as the `azure-devops` skill (that token now also carries the
Code (Write) scope required for the likes endpoints), rather than storing a
second copy of the secret.

Config via environment variables (same defaults as the azure-devops skill):
  AZDO_ORG       Azure DevOps organization name (default: diversus)
  AZDO_PROJECT   Azure DevOps project name (default: "Huddler - Product")
  AZDO_PAT_FILE  Path to a file containing the PAT (default: the azure-devops
                 skill's .pat file)
  AZDO_PAT       Inline PAT value (overrides AZDO_PAT_FILE)

Usage:
  pr-like.py list-comments <repo> <pr-id>
  pr-like.py like <repo> <pr-id> <thread-id> <comment-id>
  pr-like.py unlike <repo> <pr-id> <thread-id> <comment-id>
  pr-like.py likes <repo> <pr-id> <thread-id> <comment-id>
"""

import base64
import json
import os
import sys
import urllib.request
import urllib.parse
import urllib.error

API_VERSION = "7.1"


def find_pat_file():
    env_file = os.environ.get("AZDO_PAT_FILE")
    if env_file and os.path.isfile(env_file):
        return env_file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Shared with the azure-devops skill, which lives alongside this one
    # under ~/.pi/agent/skills/.
    shared = os.path.join(
        os.path.dirname(os.path.dirname(script_dir)), "azure-devops", ".pat"
    )
    if os.path.isfile(shared):
        return shared
    return None


def get_config():
    org = os.environ.get("AZDO_ORG", "diversus")
    project = os.environ.get("AZDO_PROJECT", "Huddler - Product")

    pat = os.environ.get("AZDO_PAT")
    if not pat:
        pat_file = find_pat_file()
        if not pat_file:
            sys.exit("error: no PAT found. Set AZDO_PAT or AZDO_PAT_FILE.")
        with open(pat_file) as f:
            pat = f.read().strip()
        if not pat or pat == "PASTE_YOUR_PAT_HERE":
            sys.exit(f"error: {pat_file} has no real token in it yet.")

    return {"org": org, "project": project, "pat": pat}


def request(cfg, method, url, body=None):
    token = base64.b64encode(f":{cfg['pat']}".encode()).decode()
    headers = {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    data = json.dumps(body).encode() if body is not None else b""
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        detail = e.read().decode()
        sys.exit(f"error: {e.code} {e.reason} for {url}\n{detail}")


def project_url(cfg, path):
    return (
        f"https://dev.azure.com/{urllib.parse.quote(cfg['org'])}/"
        f"{urllib.parse.quote(cfg['project'])}/{path}"
    )


def comment_likes_url(cfg, repo, pr_id, thread_id, comment_id):
    return project_url(
        cfg,
        f"_apis/git/repositories/{urllib.parse.quote(repo)}/pullRequests/{pr_id}/"
        f"threads/{thread_id}/comments/{comment_id}/likes?api-version={API_VERSION}",
    )


def cmd_list_comments(cfg, args):
    """List threads/comments with their ids, so a target can be picked."""
    repo, pr_id = args[0], args[1]
    url = project_url(
        cfg,
        f"_apis/git/repositories/{urllib.parse.quote(repo)}/pullRequests/{pr_id}/"
        f"threads?api-version={API_VERSION}",
    )
    result = request(cfg, "GET", url)
    for thread in result.get("value", []):
        for c in thread.get("comments", []):
            if c.get("commentType") == "system":
                continue
            author = c.get("author", {}).get("displayName", "unknown")
            print(
                f"thread {thread['id']} comment {c['id']} ({author}): "
                f"{c.get('content', '').strip()}"
            )


def cmd_like(cfg, args):
    repo, pr_id, thread_id, comment_id = args[0], args[1], args[2], args[3]
    url = comment_likes_url(cfg, repo, pr_id, thread_id, comment_id)
    request(cfg, "POST", url)
    print(f"Liked comment {comment_id} in thread {thread_id} (PR {pr_id}, {repo})")


def cmd_unlike(cfg, args):
    repo, pr_id, thread_id, comment_id = args[0], args[1], args[2], args[3]
    url = comment_likes_url(cfg, repo, pr_id, thread_id, comment_id)
    request(cfg, "DELETE", url)
    print(f"Unliked comment {comment_id} in thread {thread_id} (PR {pr_id}, {repo})")


def cmd_likes(cfg, args):
    repo, pr_id, thread_id, comment_id = args[0], args[1], args[2], args[3]
    url = comment_likes_url(cfg, repo, pr_id, thread_id, comment_id)
    result = request(cfg, "GET", url)
    for identity in result.get("value", []) if result else []:
        print(identity.get("displayName", "unknown"))


COMMANDS = {
    "list-comments": cmd_list_comments,
    "like": cmd_like,
    "unlike": cmd_unlike,
    "likes": cmd_likes,
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        sys.exit(f"usage: pr-like.py <{'|'.join(COMMANDS)}> ...")
    cfg = get_config()
    COMMANDS[sys.argv[1]](cfg, sys.argv[2:])


if __name__ == "__main__":
    main()
