#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
RUNTIME_DIR="$ROOT_DIR/.runtime"
BACKEND_PID_FILE="$RUNTIME_DIR/backend.pid"
FRONTEND_PID_FILE="$RUNTIME_DIR/frontend.pid"
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-8080}"
BACKEND_HOST="${BACKEND_HOST:-127.0.0.1}"
FRONTEND_HOST="${FRONTEND_HOST:-127.0.0.1}"
# Lifespan loads the embedding model (can be slow on first HuggingFace download) and may hit MongoDB.
BACKEND_HEALTH_WAIT_SECONDS="${BACKEND_HEALTH_WAIT_SECONDS:-180}"

log() { echo "[start] $*"; }
err() { echo "[start] $*" >&2; }

is_running() {
  local pid_file="$1"
  if [[ ! -f "$pid_file" ]]; then
    return 1
  fi
  local pid
  pid="$(cat "$pid_file")"
  kill -0 "$pid" 2>/dev/null
}

port_in_use() {
  local port="$1"
  if command -v ss >/dev/null 2>&1; then
    ss -ltn "( sport = :$port )" 2>/dev/null | grep -q ":$port"
    return $?
  fi
  if command -v lsof >/dev/null 2>&1; then
    lsof -iTCP:"$port" -sTCP:LISTEN -t >/dev/null 2>&1
    return $?
  fi
  return 1
}

cd "$ROOT_DIR"
mkdir -p "$RUNTIME_DIR" backend/logs

if is_running "$BACKEND_PID_FILE"; then
  err "Backend already running (PID $(cat "$BACKEND_PID_FILE")). Run scripts/stop.sh first."
  exit 1
fi

if [[ -f "$FRONTEND_PID_FILE" ]] && is_running "$FRONTEND_PID_FILE"; then
  err "Frontend already running (PID $(cat "$FRONTEND_PID_FILE")). Run scripts/stop.sh first."
  exit 1
fi

if port_in_use "$BACKEND_PORT"; then
  err "Port $BACKEND_PORT is already in use."
  exit 1
fi

if port_in_use "$FRONTEND_PORT"; then
  err "Port $FRONTEND_PORT is already in use."
  exit 1
fi

log "Checking dependencies..."
command -v python3 >/dev/null 2>&1 || { err "python3 is required"; exit 1; }
command -v flutter >/dev/null 2>&1 || { err "flutter is required"; exit 1; }
command -v curl >/dev/null 2>&1 || { err "curl is required"; exit 1; }

if [[ -f backend/.env ]]; then
  log "Loading backend/.env"
  set -a
  # shellcheck disable=SC1091
  . backend/.env
  set +a
fi

log "Preparing backend virtualenv..."
if [[ ! -d backend/.venv ]]; then
  python3 -m venv backend/.venv
fi
backend_python="$ROOT_DIR/backend/.venv/bin/python"
backend_uvicorn="$ROOT_DIR/backend/.venv/bin/uvicorn"

"$backend_python" -m pip install --upgrade pip >/dev/null 2>&1
"$backend_python" -m pip install -r backend/requirements.txt >/dev/null 2>&1
"$backend_python" -m pip install alembic >/dev/null 2>&1

if [[ -f backend/alembic.ini ]]; then
  log "Running database migrations..."
  if [[ -z "${DATABASE_URL:-}" ]]; then
    err "Warning: DATABASE_URL not set; alembic uses backend/alembic.ini or may fail."
  fi
  (cd backend && "$backend_python" -m alembic -c alembic.ini upgrade head) \
    || err "Alembic migration failed (non-fatal)."
fi

log "Starting backend on http://${BACKEND_HOST}:${BACKEND_PORT} ..."
(
  cd backend
  nohup "$backend_uvicorn" main:app --host "$BACKEND_HOST" --port "$BACKEND_PORT" \
    >>"$ROOT_DIR/backend/logs/uvicorn.out" 2>&1 &
  echo $! >"$BACKEND_PID_FILE"
)

BACKEND_PID="$(cat "$BACKEND_PID_FILE")"
log "Backend PID: $BACKEND_PID"

log "Waiting for backend /health (up to ${BACKEND_HEALTH_WAIT_SECONDS}s; first start can be slow) ..."
healthy=0
elapsed=0
while (( elapsed < BACKEND_HEALTH_WAIT_SECONDS )); do
  if curl -sf "http://${BACKEND_HOST}:${BACKEND_PORT}/health" >/dev/null 2>&1; then
    healthy=1
    break
  fi
  if (( elapsed > 0 && elapsed % 20 == 0 )); then
    log "Still waiting for /health (${elapsed}s / ${BACKEND_HEALTH_WAIT_SECONDS}s)..."
  fi
  sleep 1
  elapsed=$((elapsed + 1))
done

if [[ "$healthy" -ne 1 ]]; then
  err "Backend did not respond to GET /health within ${BACKEND_HEALTH_WAIT_SECONDS}s."
  err "Often this is SentenceTransformer(all-MiniLM-L6-v2) loading or downloading models; bump BACKEND_HEALTH_WAIT_SECONDS if needed."
  err "Logs: backend/logs/uvicorn.out"
  exit 1
fi
log "Backend is healthy"

if [[ ! -d frontend ]]; then
  err "No frontend/ directory found; backend only is running."
  log "API:  http://${BACKEND_HOST}:${BACKEND_PORT}"
  log "Docs: http://${BACKEND_HOST}:${BACKEND_PORT}/docs"
  log "Stop: scripts/stop.sh"
  exit 0
fi

log "Building Flutter web frontend..."
(
  cd frontend
  flutter pub get >/dev/null
  flutter build web --dart-define=API_BASE_URL="http://${BACKEND_HOST}:${BACKEND_PORT}"
)

log "Starting frontend on http://${FRONTEND_HOST}:${FRONTEND_PORT} ..."
(
  cd frontend
  nohup python3 -m http.server "$FRONTEND_PORT" \
    --bind "$FRONTEND_HOST" \
    --directory build/web \
    >>"$ROOT_DIR/.runtime/frontend.log" 2>&1 &
  echo $! >"$FRONTEND_PID_FILE"
)

FRONTEND_PID="$(cat "$FRONTEND_PID_FILE")"
log "Frontend PID: $FRONTEND_PID"

log "Application is running."
log "  Frontend: http://${FRONTEND_HOST}:${FRONTEND_PORT}"
log "  API:      http://${BACKEND_HOST}:${BACKEND_PORT}"
log "  API docs: http://${BACKEND_HOST}:${BACKEND_PORT}/docs"
log "Stop with: scripts/stop.sh"
