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
