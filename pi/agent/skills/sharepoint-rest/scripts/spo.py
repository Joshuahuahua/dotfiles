#!/usr/bin/env python3
"""Live SharePoint Online REST testing via device-code OAuth.

No extra dependencies - stdlib only (urllib). Caches tokens next to this
script so the device-code flow only has to be repeated when the refresh
token itself expires (Azure AD default ~90 days of inactivity).
"""
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.environ.get("SPO_TOKEN_CACHE") or os.path.join(SCRIPT_DIR, "..", ".token_cache.json")
CACHE_FILE = os.path.abspath(CACHE_FILE)

TENANT_ID = os.environ.get("SPO_TENANT_ID", "fa17b8ee-13de-4039-84de-200564f4fcfe")
# Well-known "SharePoint Online Management Shell" first-party app id. This one
# is pre-registered/consented in the tenant; the PnP Management Shell id
# (31359c7f-bd7e-475c-86db-fdb8c937548e) is NOT and fails with AADSTS700016.
CLIENT_ID = os.environ.get("SPO_CLIENT_ID", "9bc3ab49-b65d-410a-85ad-de819febfddc")
TENANT_HOST = os.environ.get("SPO_TENANT_HOST", "huddler365.sharepoint.com")
DEFAULT_SITE = os.environ.get("SPO_DEFAULT_SITE", "huddler-integration")

AUTH_BASE = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0"
RESOURCE = f"https://{TENANT_HOST}"
SCOPE = f"{RESOURCE}/.default offline_access"


def _post_form(url, data):
    body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        try:
            err = json.loads(e.read().decode())
        except Exception:
            err = {"error": str(e)}
        return err


def _load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE) as f:
            return json.load(f)
    return {}


def _save_cache(data):
    with open(CACHE_FILE, "w") as f:
        json.dump(data, f)
    os.chmod(CACHE_FILE, 0o600)


def login():
    """Start the device-code flow. Opens the verification URL in the browser,
    copies the user code to the clipboard, then polls until the user
    approves it and saves the resulting tokens."""
    resp = _post_form(f"{AUTH_BASE}/devicecode", {
        "client_id": CLIENT_ID,
        "scope": SCOPE,
    })
    if "device_code" not in resp:
        print(f"Error starting device code flow: {resp}", file=sys.stderr)
        sys.exit(1)

    print(resp["message"])
    verification_uri = resp.get("verification_uri", "https://login.microsoftonline.com/common/oauth2/deviceauth")
    user_code = resp.get("user_code", "")

    try:
        subprocess.Popen(["xdg-open", verification_uri],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass
    if user_code:
        try:
            p = subprocess.Popen(["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE)
            p.communicate(user_code.encode())
        except Exception:
            pass

    interval = resp.get("interval", 5)
    expires = time.time() + resp.get("expires_in", 900)

    while time.time() < expires:
        time.sleep(interval)
        tok = _post_form(f"{AUTH_BASE}/token", {
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            "client_id": CLIENT_ID,
            "device_code": resp["device_code"],
        })
        if "access_token" in tok:
            tok["obtained_at"] = time.time()
            _save_cache(tok)
            print("Login successful, tokens cached.")
            return
        err = tok.get("error")
        if err == "authorization_pending":
            continue
        if err == "slow_down":
            interval += 5
            continue
        print(f"Login failed: {tok}", file=sys.stderr)
        sys.exit(1)

    print("Device code expired before approval - try again.", file=sys.stderr)
    sys.exit(1)


def _refresh(cache):
    tok = _post_form(f"{AUTH_BASE}/token", {
        "grant_type": "refresh_token",
        "client_id": CLIENT_ID,
        "refresh_token": cache["refresh_token"],
        "scope": SCOPE,
    })
    if "access_token" not in tok:
        return None
    tok["obtained_at"] = time.time()
    _save_cache(tok)
    return tok


def get_token():
    """Return a valid access token, refreshing if needed. Exits with a clear
    message telling the user to approve a device-code login if there is no
    usable refresh token yet."""
    cache = _load_cache()
    if not cache:
        print("No cached tokens yet - run `login` first (requires the user "
              "to approve a device code in the browser).", file=sys.stderr)
        sys.exit(1)

    age = time.time() - cache.get("obtained_at", 0)
    if age < cache.get("expires_in", 0) - 60:
        return cache["access_token"]

    if "refresh_token" in cache:
        refreshed = _refresh(cache)
        if refreshed:
            return refreshed["access_token"]

    print("Access token expired and refresh failed - run `login` again.",
          file=sys.stderr)
    sys.exit(1)


def _api_call(method, path, site, body=None, content_type="application/json;odata=nometadata"):
    token = get_token()
    url = f"{RESOURCE}/sites/{site}/_api/{path.lstrip('/')}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/json;odata=nometadata")
    if data is not None:
        req.add_header("Content-Type", content_type)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.getcode(), resp.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def cmd_get(args):
    site = args.site or DEFAULT_SITE
    code, text = _api_call("GET", args.path, site)
    print(text)
    if code >= 400:
        sys.exit(1)


def cmd_post(args):
    site = args.site or DEFAULT_SITE
    body = None
    if args.body:
        body = json.loads(args.body)
    elif args.body_file:
        with open(args.body_file) as f:
            body = json.load(f)
    code, text = _api_call("POST", args.path, site, body=body)
    print(text)
    if code >= 400:
        sys.exit(1)


def cmd_renderlist(args):
    """Convenience wrapper for the renderlistdataasstream endpoint, which is
    the exact endpoint the SPFx webparts call for CAML-based list queries."""
    site = args.site or DEFAULT_SITE
    if args.viewxml_file:
        with open(args.viewxml_file) as f:
            view_xml = f.read()
    else:
        view_xml = args.viewxml
    path = f"web/lists/getbytitle('{args.list_title}')/renderlistdataasstream"
    body = {"parameters": {"ViewXml": view_xml}}
    code, text = _api_call("POST", path, site, body=body)
    print(text)
    if code >= 400:
        sys.exit(1)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Live SharePoint Online REST testing")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("login", help="Run the device-code OAuth flow and cache tokens")

    p = sub.add_parser("get", help="GET a SPO REST path, e.g. web/lists/getbytitle('Events')?$select=Title")
    p.add_argument("path")
    p.add_argument("--site", help=f"Site path under /sites/ (default: {DEFAULT_SITE})")
    p.set_defaults(func=cmd_get)

    p = sub.add_parser("post", help="POST a SPO REST path with a JSON body")
    p.add_argument("path")
    p.add_argument("--site")
    p.add_argument("--body", help="Inline JSON body")
    p.add_argument("--body-file", help="Path to a file containing a JSON body")
    p.set_defaults(func=cmd_post)

    p = sub.add_parser("renderlist", help="Call renderlistdataasstream with a CAML ViewXml (what the SPFx webparts use)")
    p.add_argument("list_title", help="Display title of the list, e.g. Events")
    p.add_argument("--viewxml", help="Inline CAML ViewXml string")
    p.add_argument("--viewxml-file", help="Path to a file containing the ViewXml")
    p.add_argument("--site")
    p.set_defaults(func=cmd_renderlist)

    args = parser.parse_args()
    if args.cmd == "login":
        login()
    else:
        args.func(args)


if __name__ == "__main__":
    main()
