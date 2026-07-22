---
name: conversation-summary
description: Maintains a living, searchable summary of each conversation. Use throughout a conversation to record important information (file paths, decisions, changes actually made, discovered values) and keep an accurate multi-topic title. Use when the user later asks where/what something from a past conversation was.
---

# Conversation Summary

Keeps a durable summary document per conversation so information can be found
later by topic. Backed by the `conversation-summary` extension, which stores
summaries under `~/.pi/agent/summaries/<sessionId>.json` and injects the current
conversation's summary into the system prompt each turn.

Two tools:

- `update_conversation_summary` — create/refresh the current conversation's
  `title` and `summary` (full replacement each time).
- `find_conversation_summaries` — list saved **titles only** (lightweight, no
  bodies) to decide which summary is relevant.
- `read_conversation_summary` — read the full body of a specific summary you
  picked (by `sessionId` or `titleQuery`).
- `read_full_conversation` — **fallback only:** ingest the raw transcript of a
  past conversation by `sessionId` when its summary implies the detail exists
  but doesn't actually contain it. Heavy; prefer a `search` term.

## When to update (use judgement — not every message)

Do **not** update the summary on every message. Only call
`update_conversation_summary` when something durable is genuinely worth
capturing — roughly at natural checkpoints:

- **File paths / directories** that were touched or decided on.
- **Decisions** taken and **changes actually made** (not just proposed).
- **Facts / values discovered** — a hex code, a URL, a config value, a command,
  a concrete answer.
- Reaching a milestone, finishing a task, or wrapping up a topic.
- Anything you'd realistically need to answer a later question about this
  conversation.

**Skip** updating for: greetings, acknowledgements, clarifying questions,
intermediate exploration that led nowhere, restating known info, or trivial
back-and-forth. If a message adds no new durable fact, don't write.

A good rhythm is to update once a meaningful unit of work or discovery is
complete, rather than mid-step. When in doubt, batch several small developments
into one update.

## The title (update only when scope changes)

Keep the **title accurate and specific**, but only revise it when the
conversation's scope actually shifts — e.g. a genuinely new topic appears, or
the focus changes. Don't rewrite the title for every small addition.

When the conversation spans multiple topics, the title should mention **each**
of them, e.g. `"client html file changes and dark red hex code"`, so the summary
is findable by any topic later.

## Rules

- Always pass the **full updated summary** — it replaces the stored version.
  Keep it concise but complete and deduplicated.
- Do not store secrets, tokens, or credentials.
- Don't announce summary updates unless asked; just keep it current.

## Recalling past information

When the user asks something like "where is the file we changed for that
client?" or "what was that hex code from before?":

1. Call `find_conversation_summaries` with the topic as `query` — this returns
   **titles only** (cheap), so you don't ingest every summary body.
2. Pick the relevant title(s) and call `read_conversation_summary` with that
   `sessionId` (or a `titleQuery`) to load just those bodies.
3. Answer directly with the stored detail (file path, value, decision, etc.).
4. If several titles match, briefly list them and ask, or read the most likely.
   With no query, `find_conversation_summaries` lists the most recent titles.

Don't read full summaries just to list titles — `find_conversation_summaries`
already gives you titles cheaply. Only `read_conversation_summary` for the ones
you actually need.

**Fallback — raw transcript:** if the summary suggests the topic was discussed
but doesn't contain the specific detail asked for, call `read_full_conversation`
with that `sessionId` (ideally with a `search` term) to scan the original
conversation. Only do this when the summary came up short — it's a much heavier
operation than reading the summary.

Results include a `pi --session <id>` resume command if the user wants to reopen
that conversation, but the goal is usually to answer from the stored summary.
