#!/usr/bin/env bash
# Split the active tmux pane, reconnecting to the same ssh host if the pane is in an ssh session.
# Usage: ssh-split.sh <-h|-v> <pane_id> <pane_pid> <pane_path>
dir="$1"; pane="$2"; pid="$3"; path="$4"

# Preferred: target stored by the zsh ssh wrapper (see .zshrc).
target="$(tmux show-options -pqv -t "$pane" @ssh_target)"

# Fallback: parse the ssh process running under the pane's shell.
if [ -z "$target" ]; then
  ssh_pid="$(pgrep -P "$pid" -x ssh | head -n1)"
  if [ -n "$ssh_pid" ]; then
    target="$(ps -o args= -p "$ssh_pid" | sed -E 's/^[^ ]*ssh[ ]*//')"
  fi
fi

if [ -n "$target" ]; then
  tmux split-window "$dir" -c "$path" "ssh $target"
else
  tmux split-window "$dir" -c "$path"
fi
