#!/usr/bin/env python3
"""
Figma REST API helper.

Uses a personal access token (X-Figma-Token header) against Figma's public
v1 REST API. No MCP, no OAuth, no client allowlist involved.

Docs: https://www.figma.com/developers/api
"""
import argparse
import json
import os
import re
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request

API_BASE = "https://api.figma.com/v1"


def find_token():
    env = os.environ.get("FIGMA_TOKEN")
    if env:
        return env.strip()

    custom_path = os.environ.get("FIGMA_TOKEN_FILE")
    if custom_path:
        path = custom_path
    else:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".token")
        path = os.path.abspath(path)

    if not os.path.isfile(path):
        sys.exit(f"Figma token file not found: {path}")

    with open(path, "r") as f:
        token = f.read().strip()

    if not token or token == "PASTE_YOUR_FIGMA_PERSONAL_ACCESS_TOKEN_HERE":
        sys.exit(
            "Figma token is not set yet. Paste a personal access token into "
            f"{path} (Figma -> account settings -> Security -> Personal access tokens)."
        )
    return token


def api_get(path, params=None, binary=False):
    token = find_token()
    url = f"{API_BASE}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"X-Figma-Token": token})
    try:
        with urllib.request.urlopen(req) as resp:
            data = resp.read()
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        sys.exit(f"Figma API error {e.code} for {path}: {body}")
    if binary:
        return data
    return json.loads(data)


# ── URL / key parsing ────────────────────────────────────────────────────────

FILE_URL_RE = re.compile(r"figma\.com/(?:file|design|proto)/([a-zA-Z0-9]+)")


def parse_file_key(url_or_key):
    m = FILE_URL_RE.search(url_or_key)
    if m:
        return m.group(1)
    # assume it's already a bare key
    return url_or_key


def parse_node_id(url_or_id):
    """Accepts a Figma URL with ?node-id=123-456 or a bare id (123:456 / 123-456)."""
    m = re.search(r"node-id=([0-9]+[-:][0-9]+)", url_or_id)
    raw = m.group(1) if m else url_or_id
    return raw.replace("-", ":")


# ── color helpers ─────────────────────────────────────────────────────────────

def to_hex(color):
    r = round(color.get("r", 0) * 255)
    g = round(color.get("g", 0) * 255)
    b = round(color.get("b", 0) * 255)
    a = color.get("a", 1)
    if a < 1:
        return f"#{r:02x}{g:02x}{b:02x} (alpha {a:.2f})"
    return f"#{r:02x}{g:02x}{b:02x}"


def fills_summary(node):
    out = []
    for fill in node.get("fills", []) or []:
        if not fill.get("visible", True):
            continue
        if fill.get("type") == "SOLID" and "color" in fill:
            out.append(to_hex(fill["color"]))
        else:
            out.append(fill.get("type", "?"))
    return out


# ── commands ──────────────────────────────────────────────────────────────────

def cmd_whoami(args):
    data = api_get("/me")
    print(json.dumps(data, indent=2))


def cmd_file(args):
    key = parse_file_key(args.file)
    data = api_get(f"/files/{key}", params={"depth": args.depth} if args.depth else None)
    if args.json:
        print(json.dumps(data, indent=2))
        return
    doc = data.get("document", {})
    print(f"Name: {data.get('name')}")
    print(f"Last modified: {data.get('lastModified')}")
    print(f"Version: {data.get('version')}")
    _print_tree(doc, max_depth=args.depth or 3)


def _print_tree(node, depth=0, max_depth=3):
    if depth > max_depth:
        return
    indent = "  " * depth
    line = f"{indent}- {node.get('name')} [{node.get('type')}] id={node.get('id')}"
    fills = fills_summary(node)
    if fills:
        line += f" fills={fills}"
    print(line)
    for child in node.get("children", []) or []:
        _print_tree(child, depth + 1, max_depth)


def cmd_node(args):
    key = parse_file_key(args.target)
    node_id = parse_node_id(args.target if not args.node_id else args.node_id)
    data = api_get(f"/files/{key}/nodes", params={"ids": node_id})
    nodes = data.get("nodes", {})
    if args.json:
        print(json.dumps(nodes, indent=2))
        return
    for nid, wrapper in nodes.items():
        doc = wrapper.get("document", {})
        print(f"Node {nid}:")
        _print_tree(doc, max_depth=args.depth or 4)
        _print_text_and_styles(doc)


def _print_text_and_styles(node, path=""):
    label = f"{path}/{node.get('name')}" if path else node.get("name", "")
    if node.get("type") == "TEXT":
        chars = node.get("characters", "")
        style = node.get("style", {})
        font = style.get("fontFamily")
        size = style.get("fontSize")
        weight = style.get("fontWeight")
        print(f"  TEXT [{label}]: \"{chars}\" ({font}, {size}px, weight {weight})")
    for child in node.get("children", []) or []:
        _print_text_and_styles(child, label)


def cmd_styles(args):
    key = parse_file_key(args.file)
    data = api_get(f"/files/{key}/styles")
    print(json.dumps(data.get("meta", data), indent=2))


def cmd_image(args):
    key = parse_file_key(args.target)
    node_id = parse_node_id(args.target if not args.node_id else args.node_id)
    data = api_get(
        f"/images/{key}",
        params={"ids": node_id, "format": args.format, "scale": args.scale},
    )
    images = data.get("images", {})
    url = images.get(node_id)
    if not url:
        sys.exit(f"No image URL returned for node {node_id}: {data}")
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        content = resp.read()
    suffix = f".{args.format}"
    fd, path = tempfile.mkstemp(prefix="figma_", suffix=suffix)
    with os.fdopen(fd, "wb") as f:
        f.write(content)
    print(path)


def main():
    parser = argparse.ArgumentParser(description="Figma REST API helper")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("whoami", help="Check the token works, show account info")
    p.set_defaults(func=cmd_whoami)

    p = sub.add_parser("file", help="Fetch a whole file's document tree")
    p.add_argument("file", help="Figma file URL or file key")
    p.add_argument("--depth", type=int, default=None)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_file)

    p = sub.add_parser("node", help="Fetch one node (frame/layer) by URL with ?node-id= or key+id")
    p.add_argument("target", help="Figma URL (with node-id) or file key")
    p.add_argument("--node-id", default=None, help="Override/-provide node id (123:456)")
    p.add_argument("--depth", type=int, default=None)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_node)

    p = sub.add_parser("styles", help="List a file's published styles (colors, text, effects)")
    p.add_argument("file", help="Figma file URL or file key")
    p.set_defaults(func=cmd_styles)

    p = sub.add_parser("image", help="Render a node to an image file and print its local path")
    p.add_argument("target", help="Figma URL (with node-id) or file key")
    p.add_argument("--node-id", default=None)
    p.add_argument("--format", default="png", choices=["png", "svg", "jpg", "pdf"])
    p.add_argument("--scale", type=float, default=2)
    p.set_defaults(func=cmd_image)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
