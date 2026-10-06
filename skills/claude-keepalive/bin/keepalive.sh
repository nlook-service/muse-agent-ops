#!/bin/bash
# claude-keepalive.sh — keeps the Claude Code remote-control session alive.
# Runs every 5 min via cron. If the tmux session or claude process is gone
# (e.g. after a VM restart), restarts it with --continue so the previous
# conversation is resumed. Then auto-confirms the workspace trust prompt.
set -u

CLAUDE_BIN="$HOME/.local/bin/claude"
SESSION="claude"
LOG="$HOME/workspace/claude-keepalive/keepalive.log"
LOCKDIR="$HOME/workspace/claude-keepalive/.lock"

log() { echo "$(date '+%F %T') $*" >> "$LOG"; }

# single-instance guard
if ! mkdir "$LOCKDIR" 2>/dev/null; then
  exit 0
fi
trap 'rmdir "$LOCKDIR"' EXIT

alive=0
if tmux has-session -t "$SESSION" 2>/dev/null && pgrep -f "[c]laude( |$)" >/dev/null; then
  alive=1
fi

if [ "$alive" -eq 1 ]; then
  exit 0
fi

log "session down — restarting claude with --continue"
tmux kill-session -t "$SESSION" 2>/dev/null
sleep 2
tmux new-session -d -s "$SESSION" -x 140 -y 40 "$CLAUDE_BIN --continue" >>"$LOG" 2>&1

# wait for the workspace-trust prompt and confirm it
for i in $(seq 1 6); do
  sleep 5
  if tmux capture-pane -t "$SESSION" -p 2>/dev/null | grep -q "Is this a project you created"; then
    tmux send-keys -t "$SESSION" Down Enter
    log "confirmed workspace trust prompt"
    break
  fi
done

if pgrep -f "[c]laude( |$)" >/dev/null; then
  log "restart ok"
else
  log "restart FAILED — manual check needed"
fi
