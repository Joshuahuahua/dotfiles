---
name: clipboard
description: Copies text to Josh's system clipboard using xclip (X11). Use whenever asked to "copy this", "put that on my clipboard", "copy the link/output/text", etc.
---

# Clipboard

Josh is on an X11 session with `xclip` installed. Use it to copy text to the
system clipboard whenever asked to "copy this", "copy that to my clipboard",
etc.

## Copy text to clipboard

```bash
printf '%s' "the text to copy" | xclip -selection clipboard
```

- Use `printf '%s'` (not `echo`) to avoid adding a trailing newline unless one
  is wanted, and to avoid interpreting backslashes.
- For multi-line content, pipe it in via a heredoc instead:
  ```bash
  xclip -selection clipboard <<'EOF'
  line one
  line two
  EOF
  ```
- To copy the output of another command directly:
  ```bash
  some-command | xclip -selection clipboard
  ```

## Verify what's on the clipboard

```bash
xclip -selection clipboard -o
```

Useful to confirm a copy worked, or to read back what's currently there if
asked.

## Notes

- Always use `-selection clipboard` (the "Ctrl+C / Ctrl+V" clipboard), not
  the default X11 primary selection, unless Josh asks specifically for the
  primary/middle-click selection (`-selection primary`).
- `xclip` needs an X11 display; this is Josh's setup (`XDG_SESSION_TYPE=x11`),
  so no extra flags are needed.
- If a request implies copying a value produced by another skill/tool (e.g. a
  PR URL from the azure-devops skill, a work item title, printer output),
  generate that value first, then pipe/copy it — don't ask the user to
  restate it if it's already known from context.
