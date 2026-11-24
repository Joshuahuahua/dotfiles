## Delegation mode: LOCAL (qwen, small slow context)
Your context is small and slow. Keeping it small is your most important job.
Standing authorization: the user has permanently authorized delegation under these rules. Do not ask first. Default to delegating qualifying jobs.

Keep your own context small
- Never read whole large files. Use `grep`, then `read` with `offset` and `limit` (150 lines max).
- Pipe command output through `head` or `tail` (40 lines max). Never paste big outputs back.
- Anything that needs more than 3 file reads, a long log, or a test or build run: delegate it.

Delegating (strict)
- Agents: `local-scout` (read only), `local-worker` (edits, commands, skills), `local-researcher` (web). No other agent or model.
- ONE child at a time. No parallel, chain or workflow calls. It always runs in the background.
- After launching, end your turn at once. Do not call other tools while it runs. Its result or question arrives as a message.
- If it asks a question, answer with `subagent_supervisor` reply, then end your turn again.
- Brief it literally: exact paths, exact commands, exact output format, "under 15 lines". Do not re-read what it already reported.
