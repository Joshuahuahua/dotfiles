# Persistent Assistant Memory

## Stable user preferences
- Wants the assistant to maintain memory across sessions.
- Memory must live outside individual repos and work across projects.
- When building cross-project assistant tooling, prefer user-level files/config under the home directory instead of writing into the current repo.
- Prefer not to use references to Claude-branded files, concepts, or terminology unless strictly necessary to describe existing system behavior.

## Memory rules
- Store durable preferences, long-lived workflow notes, and user-approved facts that improve future sessions.
- Do not store secrets, tokens, passwords, or other sensitive credentials.
- Keep entries concise, factual, and deduplicated.
- If a possible memory is ambiguous or temporary, ask before saving it.

## Remembered items
- Keep project and global memory aligned with current implementation. When work changes a previously saved durable fact or workflow, update the relevant memory entry so it matches the new state instead of leaving stale notes. _(saved 2026-07-14)_

## Remembered items
- User wants a personal todo-list workflow in Pi: when they ask to remember tasks, store them in a todo list; when work may satisfy an existing todo, ask afterward whether to remove, mark done, or update the item. _(saved 2026-07-14)_

## Remembered items
- User wants Pi startup UI to include current open todo list items from the todo-list workflow. _(saved 2026-07-14)_
