# Managed Pi agent files

This directory contains the **repo-managed subset** of `~/.pi/agent/` that is safe to sync via dotfiles.

Included here:
- `AGENTS.md`
- `settings.json`
- `extensions/`
- `memory/`

Intentionally **not** included here:
- `auth.json`
- `sessions/`
- other transient/runtime files that should remain local

The Mint bootstrap script is intended to symlink this managed subset back into `~/.pi/agent/` file-by-file/directory-by-directory, while leaving auth and session data local.
