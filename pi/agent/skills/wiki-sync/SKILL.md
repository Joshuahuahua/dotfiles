---
name: wiki-sync
description: Pulls the latest Huddler wiki content and refreshes the locally-tracked coding standards used automatically for all Huddler product work. Use whenever the user asks to "check for updates to the wiki", "sync the wiki", "pull the wiki", or similar.
---

# Wiki Sync (Huddler coding standards)

Keeps the locally-mirrored coding standards (used automatically as project
context any time work happens in the Huddler product repo) in sync with the
source wiki page, which is updated by the team from time to time.

## Background / how the standards get applied automatically

- Source of truth: the wiki page
  `Infrastructure-(Internal)/Coding-Standards-+-Guiding-Principals.md` in the
  wiki repo at `/home/josh/development/work/huddler/Wiki`.
- Canonical mirrored copy: `/home/josh/development/clones/dotfiles/pi/agent/product-context/huddler-coding-standards.md`
  (tracked/committed in the dotfiles repo, with a header comment recording
  which wiki commit it was last synced from).
- That canonical file is **symlinked as `AGENTS.md`** into the root of each
  Huddler product working copy:
  - `/home/josh/development/work/huddler/hub/workspace1/AGENTS.md`
  - `/home/josh/development/work/huddler/hub/workspace2/AGENTS.md`
  - `/home/josh/development/work/huddler/hub/workspace3/AGENTS.md`
  - Each symlink is listed in that workspace's `.git/info/exclude` (a purely
    local git-ignore, not the shared `.gitignore`), so it never shows up as
    untracked/gets committed to the shared repo.
  - Pi auto-discovers `AGENTS.md` by walking up from the current working
    directory, so any work done anywhere inside workspace1/2/3 automatically
    picks up the current coding standards as project context — no memory
    lookup or explicit reminder needed.
- Because of this, **this skill only needs to update one file** (the
  canonical copy in dotfiles) to refresh standards everywhere.

## Process

1. **Pull the wiki repo:**
   ```bash
   cd /home/josh/development/work/huddler/Wiki && git pull
   ```

2. **Check the last-synced commit** recorded in the header comment of
   `/home/josh/development/clones/dotfiles/pi/agent/product-context/huddler-coding-standards.md`
   (a line like `Synced from wiki commit: <hash> (<date>)`).

3. **Check for changes since that commit:**
   ```bash
   cd /home/josh/development/work/huddler/Wiki
   git log --format="%H %ci" -- "Infrastructure-(Internal)/Coding-Standards-+-Guiding-Principals.md"
   git diff <last_synced_hash> HEAD -- "Infrastructure-(Internal)/Coding-Standards-+-Guiding-Principals.md"
   ```

4. **If there's no diff:** tell the user the standards are already up to date
   (mention the commit/date checked) and stop.

5. **If there is a diff:**
   - Regenerate the canonical file: keep the header comment block (update the
     `Synced from wiki commit:` line to the new hash/date), followed by the
     full current contents of the wiki page, e.g.:
     ```bash
     cd /home/josh/development/clones/dotfiles
     { head -n <N> pi/agent/product-context/huddler-coding-standards.md; \  # keep header, adjust as needed
       cat "/home/josh/development/work/huddler/Wiki/Infrastructure-(Internal)/Coding-Standards-+-Guiding-Principals.md"; \
     } > pi/agent/product-context/huddler-coding-standards.md
     ```
     (Simplest: just rewrite the whole file with the `write` tool — header
     comment block + fresh wiki content appended — rather than fiddling with
     `head`/`cat` line counts.)
   - Commit it in dotfiles:
     ```bash
     cd /home/josh/development/clones/dotfiles
     git add pi/agent/product-context/huddler-coding-standards.md
     git commit -m "product-context: sync Huddler coding standards from wiki (<short-hash>)"
     ```
   - **Summarize what changed** to the user in plain English (based on the
     diff) — don't just say "it changed", actually describe the added/
     removed/modified rules.

## Notes

- This only tracks the one Coding Standards page today. If asked to also
  track other wiki pages the same way, extend this same pattern (new
  canonical file in `pi/agent/product-context/`, new symlink target note
  here) rather than inventing a different mechanism.
- Never push the dotfiles commit automatically — commit locally only, per
  usual dotfiles workflow, unless explicitly asked to push.
- If new workspaces (workspace4, etc.) are added later, remember to add the
  same `AGENTS.md` symlink + `.git/info/exclude` entry for them too.
