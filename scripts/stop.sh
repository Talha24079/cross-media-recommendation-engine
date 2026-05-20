#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
RUNTIME_DIR="$ROOT_DIR/.runtime"
BACKEND_PID_FILE="$RUNTIME_DIR/backend.pid"
FRONTEND_PID_FILE="$RUNTIME_DIR/frontend.pid"
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-8080}"

log() { echo "[stop] $*"; }
err() { echo "[stop] $*" >&2; }

stop_pid() {
  local name="$1"
  local pid_file="$2"

  if [[ ! -f "$pid_file" ]]; then
    log "No PID file for $name ($pid_file)"
    return 0
  fi

  local pid
  pid="$(cat "$pid_file" 2>/dev/null || true)"
  if [[ -z "$pid" ]]; then
    rm -f "$pid_file"
    return 0
  fi

  if kill -0 "$pid" 2>/dev/null; then
    log "Stopping $name (PID $pid)..."
    kill -TERM "$pid" 2>/dev/null || true
    for _ in $(seq 1 10); do
      if ! kill -0 "$pid" 2>/dev/null; then
        break
      fi
      sleep 0.5
    done
    if kill -0 "$pid" 2>/dev/null; then
      log "Force killing $name (PID $pid)..."
      kill -KILL "$pid" 2>/dev/null || true
    fi
  else
    log "$name PID $pid is not running"
  fi

  rm -f "$pid_file"
}

stop_port() {
  local port="$1"
  local pids=""

  if command -v lsof >/dev/null 2>&1; then
    pids="$(lsof -tiTCP:"$port" -sTCP:LISTEN 2>/dev/null || true)"
  elif command -v fuser >/dev/null 2>&1; then
    pids="$(fuser -n tcp "$port" 2>/dev/null || true)"
  fi

  if [[ -z "$pids" ]]; then
    return 0
  fi

  log "Stopping process(es) on port $port: $pids"
  # shellcheck disable=SC2086
  kill -TERM $pids 2>/dev/null || true
  sleep 1
  # shellcheck disable=SC2086
  kill -KILL $pids 2>/dev/null || true
}

log "Stopping Cross-Media Recommendation Engine..."

stop_pid "frontend" "$FRONTEND_PID_FILE"
stop_pid "backend" "$BACKEND_PID_FILE"

stop_port "$FRONTEND_PORT"
stop_port "$BACKEND_PORT"

log "Application stopped."
