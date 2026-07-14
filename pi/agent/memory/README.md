# Assistant Memory System

This directory provides persistent memory for the coding assistant across sessions and projects.

## Files
- `MEMORY.md` — global durable memory shared across projects.
- `projects/` — optional project-specific notes stored outside repos.
- `bin/memory.py` — small CLI for viewing and updating memory.
- `../extensions/persistent-memory.ts` — pi extension that injects memory into prompts.

## Usage
Show memory:

```bash
python3 ~/.pi/agent/memory/bin/memory.py show
```

Add a global memory item:

```bash
python3 ~/.pi/agent/memory/bin/memory.py add-global "Prefer pnpm over npm"
```

Add a project memory item for the current working directory:

```bash
python3 ~/.pi/agent/memory/bin/memory.py add-project "This repo uses generated API clients; do not edit them by hand"
```

Print the project memory path for the current working directory:

```bash
python3 ~/.pi/agent/memory/bin/memory.py project-path
```

## Notes
- Memory is intentionally stored outside repos in the default setup.
- In this dotfiles repo, the managed `pi/agent/` subset can be symlinked back into `~/.pi/agent/` if desired.
- The pi extension automatically loads this memory into future prompts/sessions.
- Project notes are keyed by working-directory path.
- The extension also adds `/remember <text>`, `/remember-project <text>`, and the `remember_memory` tool.
- Restart pi or reload extensions after installing/changing the extension.
