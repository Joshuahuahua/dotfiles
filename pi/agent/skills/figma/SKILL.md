---
name: figma
description: Reads Figma design files (structure, layers, colors, typography, and rendered images) using Figma's public REST API and a personal access token. Use when asked to inspect/read a Figma file or frame, get design context/tokens (colors, spacing, fonts) from a Figma link, get a screenshot/render of a Figma frame, or implement a design from a Figma URL.
---

# Figma

Read Figma design files (document structure, layers, colors, typography, and
rendered images) using Figma's public REST API v1 and a personal access
token. This does **not** use Figma's MCP server — the remote MCP server is
gated to an allowlist of catalog clients (Cursor, Claude Code, VS Code,
etc.) that does not include Pi, and the desktop MCP server requires the
Figma desktop app, which has no Linux build. The plain REST API has no such
restriction and gives equivalent design-context data.

Use this skill whenever asked to:
- Inspect/read a Figma file or a specific frame/layer.
- Get design context (structure, colors, spacing, typography) from a Figma
  URL, so it can be implemented in code.
- Get a screenshot/render of a Figma frame or layer.
- List a file's published styles (color/text/effect tokens).

## Authentication (personal access token)

The token is kept out of git history via the dotfiles repo's `.gitignore`:

- File: `~/.pi/agent/skills/figma/.token` (resolves to
  `/home/josh/development/clones/dotfiles/pi/agent/skills/figma/.token`,
  since `~/.pi/agent/skills` is symlinked into the dotfiles repo). The
  dotfiles repo's `.gitignore` excludes `pi/agent/skills/figma/.token` — do
  not remove that entry.
- The helper script finds this file automatically next to itself. It also
  checks `FIGMA_TOKEN_FILE` (custom path) and `FIGMA_TOKEN` (inline env var)
  first.
- If the file still contains the placeholder
  `PASTE_YOUR_FIGMA_PERSONAL_ACCESS_TOKEN_HERE`, the script fails with a
  clear error — tell Josh to generate a token (Figma → account Settings →
  Security → Personal access tokens, read-only scope is enough) and paste it
  in.
- Never print the token contents, never commit this file, never paste it
  into chat.

## Helper script

Script: `scripts/figma.py` (resolve relative to this SKILL.md's directory,
i.e. `/home/josh/.pi/agent/skills/figma/scripts/figma.py`). Run it with
`python3`. No extra dependencies (stdlib only).

### Check the token works

```bash
python3 figma.py whoami
```

### Read a whole file's structure

```bash
# Accepts a full figma.com/file/... or figma.com/design/... URL, or a bare file key
python3 figma.py file "https://www.figma.com/design/<fileKey>/<name>" --depth 3
python3 figma.py file <fileKey> --json   # full raw JSON if more detail is needed
```

### Read one frame/layer (design context)

This is the most common case — Josh will usually paste a Figma link that
includes `?node-id=...` pointing at a specific frame or layer.

```bash
python3 figma.py node "https://www.figma.com/design/<fileKey>/<name>?node-id=123-456"
```

Prints a layer tree (name/type/id/fills) plus any text nodes with their
content, font family, size, and weight — enough to implement the design
directly. Add `--json` for the full raw node JSON if more structural detail
(auto-layout, constraints, effects, exact positions) is needed.

### List a file's published styles (design tokens)

```bash
python3 figma.py styles "https://www.figma.com/design/<fileKey>/<name>"
```

### Render an image of a frame/layer

```bash
python3 figma.py image "https://www.figma.com/design/<fileKey>/<name>?node-id=123-456" --scale 2
```

Prints the local file path of a downloaded PNG (or pass `--format svg|jpg|pdf`).
Use the `read` tool on that path to actually view it.

## Notes

- Figma URLs put the node id as `node-id=123-456` (hyphen); the API needs
  `123:456` (colon) — the script converts this automatically whether it's
  parsed from a URL or passed via `--node-id`.
- If a call fails with an HTTP 403, the token is likely missing/invalid, or
  Josh doesn't have access to that file. A 404 usually means a wrong file
  key or a private file the token's account can't see.
- This only supports read access (matches the read-only nature of the
  token). Writing to the canvas is out of scope.
