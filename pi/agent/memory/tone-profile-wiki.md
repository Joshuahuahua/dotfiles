# Huddler Product Wiki Tone/Style Profile

Derived from reviewing the local Huddler wiki
(/home/josh/development/work/huddler/Wiki). Use this register for
documentation output: README files, markdown docs, wiki-style pages,
architecture/process write-ups.

## Structural conventions
- Start pages with a one- or two-sentence plain overview of what the page
  covers, then a `[[_TOC_]]` marker for DevOps wiki table-of-contents (only
  relevant in the actual wiki, not repo READMEs — but keep the same
  "orient the reader first" habit in READMEs too).
- Use `##`/`###` headers to break content into clearly named sections
  (e.g. "## Branch Structure", "### 1. Master Branch (`master`)").
- Use horizontal rules (`---`) between major sections.
- Use numbered lists for sequential/ordered concepts (branch types, steps),
  bullet lists for unordered facts/details.
- Use bold for key terms/labels inline (e.g. "**Necessary to** create
  security groups...", "**Master Branch (`master`)**").
- Use `<br>` or blank lines to separate list items when extra breathing
  room helps readability in DevOps wiki rendering.
- Diagrams (Mermaid gitGraph/flowchart) are used for processes/branch
  strategy where a visual helps; include a short prose summary of the
  diagram's key events underneath as a numbered list.
- Link out to authoritative external references (Microsoft Graph docs,
  internal SharePoint sites) inline rather than re-explaining them.

## Voice/register
- Third-person, impersonal, factual — no "I" or "you" chatter; describe
  what a branch/permission/process *is* and *does*.
- Precise and justification-driven: state not just what a thing is, but
  why it's necessary ("Necessary to create security groups for Storage
  Locations.").
- Neutral, professional tone throughout — no jokes, no casual asides, no
  filler words.
- Consistent terminology: exact branch names, permission names, and
  environment names in backticks/code formatting every time they're
  referenced.
- Sentences are complete and grammatically correct (contrast with Josh's
  own casual chat register) — full stops, capitalization, proper nouns
  capitalized correctly (SharePoint, Graph API, PR, BA, etc).
- Uses a "workflow" framing for processes: describe trigger → steps →
  outcome (see Hotfix Process section) rather than a loose narrative.

## How to apply
- Use for: README.md files, wiki-style docs, architecture write-ups,
  onboarding/setup guides, any content meant to be consumed by other
  developers as reference documentation.
- Do NOT use for: chat replies, commit messages, code comments — use
  tone-profile-user.md for those instead.
