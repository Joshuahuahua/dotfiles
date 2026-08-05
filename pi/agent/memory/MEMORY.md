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
