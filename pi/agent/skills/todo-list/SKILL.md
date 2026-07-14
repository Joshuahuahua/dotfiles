---
name: todo-list
description: Maintains a personal todo list for remembered tasks. Use when the user asks to remember something they need to do, asks what tasks are still pending, wants to update/remove/tick off an item, or when a just-finished task may satisfy an existing todo and you should ask whether to remove or update it.
---

# Todo List

This skill manages the user's personal todo list at:

- skill dir: `~/.pi/agent/skills/todo-list/`
- data file: `~/.pi/agent/skills/todo-list/data/todos.json`
- helper script: `~/.pi/agent/skills/todo-list/bin/todo.py`

## When to use this skill

Use this skill when the user:

- asks you to remember a thing they need to do
- asks what they need to do / what is still pending
- asks to update, remove, complete, or reopen a todo item
- asks you to do work that may correspond to an existing todo item

## Important rules

- Do **not** use persistent memory for ordinary todo items; use this skill's todo file instead.
- Keep todo text short, clear, and action-oriented.
- Prefer one task per item.
- Do not remove or mark an item done unless the user asked for that, or clearly confirmed it.
- If a task seems like it may satisfy an existing todo, finish the work first, then ask whether they want the todo removed, marked done, or updated.
- Never store secrets or credentials in todo items.

## Standard workflow

### Add a todo

When the user says things like:

- “remember to …”
- “add this to my todo list …”
- “I need to …” and they clearly want you to remember it

run:

```bash
cd ~/.pi/agent/skills/todo-list && ./bin/todo.py add "<task>"
```

Then briefly confirm the new item.

### Show current todos

When the user asks what they need to do, run:

```bash
cd ~/.pi/agent/skills/todo-list && ./bin/todo.py list
```

If they ask for all items including completed ones:

```bash
cd ~/.pi/agent/skills/todo-list && ./bin/todo.py list --all
```

### Search for matching todos

When you suspect current work may correspond to an existing todo, check first with:

```bash
cd ~/.pi/agent/skills/todo-list && ./bin/todo.py search "<keywords>"
```

You can also just list open items if the set is small.

### Update a todo

```bash
cd ~/.pi/agent/skills/todo-list && ./bin/todo.py update <id> "<new text>"
```

Optional note:

```bash
cd ~/.pi/agent/skills/todo-list && ./bin/todo.py note <id> "<extra context>"
```

### Mark done / reopen / remove

```bash
cd ~/.pi/agent/skills/todo-list && ./bin/todo.py done <id>
cd ~/.pi/agent/skills/todo-list && ./bin/todo.py reopen <id>
cd ~/.pi/agent/skills/todo-list && ./bin/todo.py remove <id>
```

Use `done` when they want it ticked off but retained; use `remove` when they want it deleted.

## End-of-task follow-up behavior

If you complete work that appears to match an open todo item, ask a follow-up like:

- “This looks like it may satisfy todo #12 (`…`). Want me to remove it, mark it done, or update it?”

Do this **after** the work is done or plausibly done, not before.

If multiple items may match, list the likely matches and ask which one(s) to update.

## Examples

Add:

```bash
cd ~/.pi/agent/skills/todo-list && ./bin/todo.py add "renew passport"
```

List:

```bash
cd ~/.pi/agent/skills/todo-list && ./bin/todo.py list
```

Search:

```bash
cd ~/.pi/agent/skills/todo-list && ./bin/todo.py search "passport"
```
