# Compact memory (local mode)
Short rules for the small local model. Full memory: ~/.pi/agent/memory/MEMORY.md (read it only if needed).
- Never use the em dash. Use a plain hyphen. Never say "gotcha", "punt" or "circle back".
- Be concise. Do not ask follow-up questions unless truly necessary.
- "let me know" / "lemme know": use the say skill (voice only). "notify me": say skill with --notify. Never run spd-say, notify-send or kdeconnect-cli directly. Write the full answer first, then trigger it.
- Dotfiles repo: /home/josh/development/clones/dotfiles. Commit changes there proactively in small topic commits with short messages. Never push unless asked.
- Explicit approval is required before AWS CLI or Terraform commands, production changes, or terraform apply. A temp file in /tmp is fine; clean it up.
- Prefer not to use React useEffect. Keep documentation lines under ~100 columns and break after sentences.
- Use the tone profiles in ~/.pi/agent/memory/tone-profile-{user,wiki}.md for chat/commits and documentation respectively.
- The remember_memory tool saves durable facts only when the user asks.
