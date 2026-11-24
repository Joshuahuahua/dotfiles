# Managed Pi agent files

This directory contains the **repo-managed subset** of `~/.pi/agent/` that is safe to sync via dotfiles.

## How the symlinks work

Each file/directory below lives for real in this repo (`pi/agent/...`). The matching path under
`~/.pi/agent/` is a **symlink pointing back into this repo**, not a copy. That means editing either
side edits the same underlying file — Pi reads/writes through the symlink at
`~/.pi/agent/...`, and `git status`/`git commit` in this repo picks up the change because it's the
same inode the symlink resolves to.

Current symlinks on this machine (`~/.pi/agent/<name>` -> `pi/agent/<name>` in this repo):

- `AGENTS.md`
- `settings.json`
- `keybindings.json`
- `web-search.json`
- `extensions/`
- `skills/`
- `memory/README.md`
- `memory/bin/`
- `memory/MEMORY.md`
- `memory/projects/`
- `memory/tone-profile-user.md`, `memory/tone-profile-wiki.md`
- `memory/MEMORY.local.md` (compact memory loaded in local qwen mode)
- `models.json`
- `subagents.json`
- `bin/`
- `agents/`
- `product-context/`

Installed Pi packages (extensions from npm) are listed in `settings.json` under `packages`.
Pi reinstalls them on startup, so only that list needs to be synced, not `npm/`.

Intentionally **not** included here:
- `auth.json`
- `sessions/`
- `web-search-cache/`
- other transient/runtime/credential files that should remain local

The Mint bootstrap script is intended to (re)create these symlinks file-by-file/directory-by-directory,
while leaving auth, session, and cache data local. If a symlink is ever missing, recreate it with:

```bash
ln -s ~/development/clones/dotfiles/pi/agent/<name> ~/.pi/agent/<name>
```

(adjust the repo path if the clone lives elsewhere).

## Claude / local qwen modes

The active model decides the mode. Provider `home-ollama` is local mode, anything else is cloud mode.

- `extensions/model-profile.ts` injects `extensions/profiles/{cloud,local}.md` and shrinks the prompt in local mode.
- `extensions/delegation-policy.ts` enforces one local child at a time (and one child total in local mode).
- `extensions/model-fallback.ts` switches to local qwen when a cloud model returns `429 quota exceeded`.
- `extensions/set-thinking.ts` lets the model change its own thinking level (cloud mode).
- `agents/`: `scout` and `worker` inherit the parent model. `local-scout`, `local-worker` and `local-researcher` are pinned to qwen.
