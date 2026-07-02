#!/usr/bin/env bash
set -euo pipefail

SSH_HOST="${SSH_BACKEND_AGENT_HOST:-ubuntu@162.19.229.31}"
REMOTE_ROOT="${SSH_BACKEND_AGENT_ROOT:-/home/ubuntu/dev-sandbox}"

if [[ "${1:-}" == "--print" ]]; then
  printf "ssh -tt %q %q\n" "$SSH_HOST" "cd '$REMOTE_ROOT' && codex resume --last --yolo"
  exit 0
fi

exec ssh -tt "$SSH_HOST" "cd '$REMOTE_ROOT' && codex resume --last --yolo"
