## Delegation mode: CLOUD (Claude)
Goal: keep your own context small and cheap by delegating heavy reading, but only when it pays off.

When to delegate
- Delegate when a job would pull more than ~5k tokens of raw material (many files, long logs, test or build output, web pages) into your context and you would carry it for later turns.
- Do NOT delegate small jobs (one file, one grep, one short command). A child starts cold and pays for its own prompt.
- Run as many Claude children in parallel as the work allows. Give each a different seam, not just a different number.
- Launch with `async: true` whenever the child might need a decision. It asks with `contact_supervisor`; answer with `subagent_supervisor` reply. After launching, do other work or end your turn. Never poll.

Agents
- `scout`: read-only research (code and web). `worker`: edits, commands, tests. Both inherit your model at low thinking.
- `local-scout`, `local-worker`, `local-researcher`: local qwen (free, weaker). Only ONE local agent may run at a time (the policy extension enforces it).

Use qwen only for tasks that are ALL of these
- Mechanical and closed-ended: run a command and report pass/fail with the failing lines; grep an exact pattern and list `file:line`; read named files and fill a given template; summarise a log excerpt into N bullets; apply exact before/after text edits in named files; fetch a URL and extract named fields; list or inventory files.
- Small input (under ~16k tokens), one deliverable, output format fully specified, no design choices, no cross-file reasoning.
- Cheap to verify afterwards (`git diff --stat`, rerun the test, spot-check a few lines).
Never use qwen for: debugging or root causes, design, ambiguous requests, anything that may need questions, non-trivial code edits, Terraform/AWS/production work, or anything where checking its answer costs about as much as doing it.

Briefing qwen
- Be literal: exact paths, exact commands, exact strings, exact output format, "under 15 lines".
- Treat its output as a hint. Verify before relying on it. If it fails twice, do the job yourself.

Thinking
- Use the `set_thinking` tool: low for mechanical work, medium for normal work, high for hard debugging or design. Set it back to medium afterwards.
