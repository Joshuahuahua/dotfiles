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

## Remembered items
- When the user says "pi update", interpret it as a direct instruction to run the Pi CLI update command to update the Pi installation, without asking for clarification. _(saved 2026-07-15)_

## Remembered items
- User's ~/.zshrc defines alias `say="spd-say"`. If the user asks to 'say' something, use `spd-say` with the provided text. _(saved 2026-07-16)_

## Remembered items
- Interpret 'say' requests by intent, not literally. Example: if the user says 'say hello to me', speak 'hello', not the full instruction. If the user asks to be told when a long-running task is done, use the remembered `say` command (`spd-say`) to announce completion. _(saved 2026-07-16)_

## Remembered items
- User's notify action should use `notify-send "title" "message"`. Choose the title and message to fit the scenario when the user asks to be notified. _(saved 2026-07-16)_

## Remembered items
- For the user's notifications, use `notify-send -u critical "title" "message"` by default, since normal timeout behavior is unreliable on their Cinnamon setup. _(saved 2026-07-16)_

## Remembered items
- When the user says 'let me know when you're done' or similar, use the remembered `say` command with a short natural completion message, not just 'done'. _(saved 2026-07-16)_

## Remembered items
- The user's products include "Huddler", "DocHQ", and "Hub". When the user asks a question about "the product", Huddler, DocHQ, or Hub, use the product-wiki skill: search the local wiki at /home/josh/development/work/huddler/Wiki by listing .md file names, shortlisting relevant articles, reading them, and answering from their content (citing the source article path). _(saved 2026-07-22, updated 2026-07-22)_

## Remembered items
- Dotfiles repo is at /home/josh/development/clones/dotfiles (contains .zshrc, pi/agent config, etc.). Whenever changes appear there (e.g. after editing memory, settings, skills, zshrc), commit them in logical/split commits by topic — but never push, unless the user explicitly asks to push. _(saved 2026-08-03)_

## Remembered items
- Distinguish user's two notification-style requests: if they say "let me know" (or similar phrasing implying being told/informed), use the voice/say command (spd-say). If they say "notify me" (or use the word 'notify'), use the desktop notification command (notify-send -u critical "title" "message"). Don't conflate the two triggers. _(saved 2026-08-04)_

## Remembered items
- User prefers minimal follow-up questions: only ask when genuinely necessary, not by default. For dotfiles/skill/config changes, always commit proactively without asking first; if a change needs adjusting afterward, amend/modify the existing commit rather than asking permission first. _(saved 2026-08-05)_

## Remembered items
- When printing standup dockets (or similar devops-printer prints), default to a real print (no --preview) unless the user explicitly says to preview or not print. _(saved 2026-08-06)_

## Remembered items
- Never ask for permission to commit dotfiles/skill/config changes — always just commit directly and proactively. Only skip committing if the user explicitly says not to. Do not ask "should I commit?" or similar confirmation questions before committing. _(saved 2026-08-10)_

## Remembered items
- User dislikes the word "punt" (e.g. for deferring work) — avoid using it; say "defer" or "mark as future work" instead. _(saved 2026-08-17)_

## Remembered items
- Whenever the user says "let me know" (in any context, not just long-running background tasks), always use the spd-say voice notification (the "say" command) to announce the result/completion, in addition to any text reply. Don't reserve it only for long tasks. _(saved 2026-08-17)_

## Remembered items
- User dislikes the phrase "gotcha" — never use it in responses. _(saved 2026-08-28)_

## Remembered items
- Two tone-profile reference files exist at ~/.pi/agent/memory/tone-profile-user.md and ~/.pi/agent/memory/tone-profile-wiki.md (built by reviewing past conversations and the Huddler wiki). Use tone-profile-user.md's voice for normal chat replies, code comments, commit messages, and PR/change descriptions. Use tone-profile-wiki.md's voice for documentation output (README.md files, wiki-style docs, architecture/setup write-ups). Read the relevant file when producing that kind of output if unsure of the exact style to match. _(saved 2026-08-28)_

## Remembered items
- Keep internal reasoning/thinking concise: use short fragments/bullets instead of full narrative sentences, don't restate tool output or context already visible, don't narrate obvious mechanical next-steps ("now I will..."), only spend reasoning on actual decision points/ambiguity/tradeoffs. This must not reduce output quality — it's purely about cutting verbose internal narration. _(saved 2026-08-28)_

## Remembered items
- Josh's Keychron K8 Pro keyboard (MAC 6C:93:08:62:3D:65) on laptop "alfie" occasionally loses Bluetooth pairing/connection (works ~99% of the time). When he asks to "fix the keyboard"/"fix my bluetooth keyboard", use the keychron-bluetooth-fix skill (~/.pi/agent/skills/keychron-bluetooth-fix/SKILL.md): remove old pairing via bluetoothctl, have him put it in pairing mode (Fn+1 ~4s), scan, then pair/trust/connect via bluetoothctl, and have him type immediately after connect (idle-disconnects within ~30-60s otherwise). Likely cause is bonding/encryption key desync (host Bluetooth restart/resume issues), not proven to be L2CAP ERTM despite that being tried once. Just run the fix steps directly, don't over-analyze root cause each time. _(saved 2026-09-07)_

## Remembered items
- Pi CLI install setup on this machine (as of 2026-09-09): Installed via the official installer (`curl -fsSL https://pi.dev/install.sh | sh`), which under the hood runs `npm install -g --ignore-scripts --min-release-age=0 @earendil-works/pi-coding-agent` using whatever Node version is active via fnm at install time. It is NOT a standalone bundled runtime — the `pi` binary/package lives inside a specific fnm-managed Node version's global npm dir: `/home/josh/.local/share/fnm/node-versions/v22.23.1/installation/{bin/pi, lib/node_modules/@earendil-works/pi-coding-agent}`. Only that one Node version (v22.23.1) has it installed; other fnm versions (v16.20.0, v18.12.1, v18.20.4, v22.15.0, v22.16.0, v22.19.0, system) do not.

fnm default was changed from v22.16.0 to v22.23.1 specifically so fresh shells resolve `pi` on PATH. Reasons pi could break again in future:
- If `fnm default` gets changed away from v22.23.1 without reinstalling pi under the new default version, `pi` will go back to "command not found" in fresh shells (per-directory `.node-version`/`.nvmrc` files still override the default and are unaffected).
- If v22.23.1 is ever uninstalled via fnm, pi goes with it.
- Previously (before this migration) pi was installed via `pnpm add -g @earendil-works/pi-coding-agent`, which produced a shim at `/home/josh/.local/share/pnpm/pi` that execs whatever `node` happens to be on PATH with no bundled runtime — this caused a crash (`SyntaxError: ... 'node:fs' does not provide an export named 'globSync'`) when an older/incompatible Node version was active. That install method has been fully removed.

Pi's actual data/config lives in `~/.pi/agent/` (sessions, summaries, memory, auth.json, models-store.json, npm/ extension deps) — this directory is independent of how the `pi` executable itself is installed and is untouched by reinstalls/migrations between install methods. Config files (`AGENTS.md`, `settings.json`, `keybindings.json`, `extensions/`, `skills/`) are symlinked from `~/.pi/agent/` into the dotfiles repo at `~/development/clones/dotfiles/pi/agent/`. `~/.zshrc` is itself a symlink to `~/development/clones/dotfiles/.zshrc` (fnm setup around line 95-102: `eval "$(fnm env --use-on-cd --shell zsh)"`).

A pre-migration backup of the entire `~/.pi/agent` directory exists at `~/pi-agent-backup-20260909-113025.tar.gz` (22.8MB) in case rollback is ever needed. _(saved 2026-09-09)_
