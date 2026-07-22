---
name: product-wiki
description: Answers questions about "the product" (our product is called Huddler) by searching the local Huddler wiki. Use whenever the user asks a question about the product / Huddler / its modules, features, setup, FAQs, or how something works. List the wiki's .md files, pick relevant ones by name, read them, and answer from their content.
---

# Product Wiki (Huddler)

Our product is called **Huddler**. When the user asks a question about "the
product", "Huddler", or any of its modules/features/setup/FAQs, answer from the
local wiki instead of guessing.

Wiki location: `/home/josh/development/work/huddler/Wiki`

The wiki is a tree of Markdown (`.md`) files. Folder and file names describe
their topic (e.g. `Huddler-Modules/`, `FAQ/`, `DevOps-Environment/`,
`Infrastructure-(Internal)/`). Treat the file names like the conversation-summary
titles: use them to shortlist likely-relevant articles before reading bodies.

## Process (similar to the conversation-summary recall flow)

1. **List the candidate files by name.** Enumerate the `.md` files and scan
   their paths/names for topics matching the question:

   ```bash
   find /home/josh/development/work/huddler/Wiki -name '*.md' -not -path '*/.git/*'
   ```

   Optionally narrow by keyword against the file paths first:

   ```bash
   find /home/josh/development/work/huddler/Wiki -name '*.md' -not -path '*/.git/*' \
     | grep -i "<keyword>"
   ```

2. **Grep the contents** when the name alone isn't enough, to find where a term
   actually appears:

   ```bash
   grep -ril "<term>" /home/josh/development/work/huddler/Wiki --include='*.md'
   ```

3. **Read the shortlisted articles** with the `read` tool and extract the
   answer. Prefer reading only the files that look relevant, not everything.

4. **Answer from the wiki content.** Cite which article(s) the answer came from
   (relative path under the Wiki) so the user can verify.

5. **If nothing relevant is found**, say so plainly rather than inventing an
   answer, and suggest the closest articles you did find.

6. **Add a References section** at the end of the response listing an Azure
   DevOps wiki URL for each article you used (see below).

## References (add at the end of any wiki-sourced answer)

Whenever you use information from the wiki, finish the response with a
`References` section that links to the source article(s) in the online Azure
DevOps wiki. The URL is a **static base** plus the article's file name (with the
`.md` extension stripped). The numeric page id and the folder path are **not**
needed.

URL template:

```
https://dev.azure.com/diversus/Huddler%20-%20Product/_wiki/wikis/Huddler---Product.wiki/<Page-Name>
```

- `<Page-Name>` = the `.md` filename with `.md` removed. File names already use
  dashes for spaces, so they map straight through.

Example: `DevOps-Environment/Branch-Naming-Conventions.md` →

```
https://dev.azure.com/diversus/Huddler%20-%20Product/_wiki/wikis/Huddler---Product.wiki/Branch-Naming-Conventions
```

Format the section as a simple list, e.g.:

```
References
- Branch Naming Conventions: https://dev.azure.com/diversus/Huddler%20-%20Product/_wiki/wikis/Huddler---Product.wiki/Branch-Naming-Conventions
```

## Rules

- Always ground product answers in the wiki files; don't rely on memory or
  assumptions for Huddler-specific behavior.
- Shortlist by file/folder name first, then read — avoid ingesting the whole
  wiki when a few articles suffice.
- Some `.md` files are empty stubs (0 bytes) or short index pages; skip stubs and
  follow into the matching folder of the same name for the real content.
- Mention the source article path(s) in your answer.
