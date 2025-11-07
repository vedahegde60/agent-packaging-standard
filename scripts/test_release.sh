#!/usr/bin/env bash
# End-to-end pre-release smoke:
# - Isolated cache/logs/registry_data
# - pytest
# - build echo-agent
# - start registry on a free port
# - publish built agent
# - e2e run via registry://
# - full cleanup on exit
set -euo pipefail

# -------- config
PY=${PY:-python3}
APS_BIN=${APS_BIN:-aps}             # assumes cli installed in current venv
EXAMPLE=${EXAMPLE:-examples/echo-agent}
PKG_OUT_DIR=${PKG_OUT_DIR:-dist}

# -------- temp dirs (isolated)
ROOT="$(pwd)"
TMPROOT="$(mktemp -d -t aps-test-release.XXXXXX)"
CACHE_DIR="$TMPROOT/cache"
LOGS_DIR="$TMPROOT/logs"
REG_DIR="$TMPROOT/registry_data"
mkdir -p "$CACHE_DIR" "$LOGS_DIR" "$REG_DIR"

# Export isolation so the CLI uses these
export APS_CACHE_DIR="$CACHE_DIR"
export APS_LOGS_DIR="$LOGS_DIR"

# -------- helpers
cleanup() {
  local ec=$?
  if [[ -n "${REG_PID:-}" ]] && ps -p "$REG_PID" >/dev/null 2>&1; then
    echo "[cleanup] stopping registry (pid=$REG_PID)"
    kill "$REG_PID" 2>/dev/null || true
    # Give it a moment, then force if needed
    sleep 0.5
    kill -9 "$REG_PID" 2>/dev/null || true
  fi
  echo "[cleanup] tmp: $TMPROOT"
  # comment next line if you want to keep artifacts for debugging:
  rm -rf "$TMPROOT"
  exit "$ec"
}
trap cleanup EXIT INT TERM

pick_free_port() {
  # portable free port finder in Python
  $PY - <<'PYCODE'
import socket, sys
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('',0))
port = s.getsockname()[1]
s.close()
print(port)
PYCODE
}

wait_for_health() {
  local url=$1
  for i in $(seq 1 50); do
    if curl -fsS "$url" >/dev/null 2>&1; then
      return 0
    fi
    sleep 0.1
  done
  echo "[error] registry health check failed: $url" >&2
  return 1
}

step() { echo; echo "=== $* ==="; }

# -------- ensure deps
step "Ensuring base tools available"
$PY -V
$PY -m pip -V
command -v "$APS_BIN" >/dev/null || { echo "[error] 'aps' not on PATH (install cli with 'pip install -e cli/')"; exit 1; }

# -------- run unit tests
step "Running unit tests (pytest -q)"
$PY -m pytest -q

# -------- build example agent
step "Building example agent package ($EXAMPLE)"
PKG_PATH="$($APS_BIN build "$EXAMPLE" --dist "$PKG_OUT_DIR" | tail -n1)"
test -f "$PKG_PATH" || { echo "[error] package not found at $PKG_PATH"; exit 1; }
echo "[ok] built: $PKG_PATH"
echo "Contents preview:"
tar -tzf "$PKG_PATH" | sed -n '1,10p'

# -------- start local registry
PORT="$(pick_free_port)"
REGISTRY_URL="http://127.0.0.1:$PORT"

step "Starting registry at $REGISTRY_URL (root=$REG_DIR)"
# run in current venv; stdout/stderr go to a log in TMPROOT
"$APS_BIN" registry serve --root "$REG_DIR" --port "$PORT" >"$TMPROOT/registry.log" 2>&1 &
REG_PID=$!
echo "[info] registry pid: $REG_PID"
sleep 0.2
wait_for_health "$REGISTRY_URL/healthz" || { echo "[error] registry failed to start"; echo "---- registry log ----"; sed -n '1,200p' "$TMPROOT/registry.log"; exit 1; }

# -------- publish
step "Publishing package to registry"
PUB_JSON="$("$APS_BIN" publish "$PKG_PATH" --registry "$REGISTRY_URL" | tail -n1)"
echo "$PUB_JSON" | jq . >/dev/null 2>&1 || true
echo "[ok] publish response: $PUB_JSON"

# Extract id/version back from the registry (prefer exact manifest if needed)
AGENT_ID="$(echo "$PUB_JSON" | $PY -c 'import sys,json;print(json.load(sys.stdin)["agent"]["id"])' 2>/dev/null || echo dev.echo)"
VERSION="$(echo "$PUB_JSON" | $PY -c 'import sys,json;print(json.load(sys.stdin)["agent"]["version"])' 2>/dev/null || echo latest)"
echo "[info] agent=$AGENT_ID version=$VERSION"

# -------- search + metadata sanity
step "Search sanity"
curl -fsS "$REGISTRY_URL/v1/search?q=$(echo "$AGENT_ID" | sed 's/.*\.//')" | tee "$TMPROOT/search.json" >/dev/null

step "Metadata sanity"
curl -fsS "$REGISTRY_URL/v1/agents/$AGENT_ID" | tee "$TMPROOT/meta.json" >/dev/null

# -------- pull & run e2e
step "Pulling agent to isolated cache"
$APS_BIN pull "$AGENT_ID" --version "$VERSION" --registry "$REGISTRY_URL"

step "E2E run from registry"
echo '{"aps_version":"0.1","operation":"run","inputs":{"text":"hello"}}' | $APS_BIN run "registry://$AGENT_ID"

# -------- stream check (best-effort)
if grep -q '"entrypoint": *"python src/echo/main.py"' "$EXAMPLE/aps/agent.yaml" 2>/dev/null || true; then
  step "E2E stream run (best-effort)"
  echo '{"aps_version":"0.1","operation":"run","inputs":{"text":"stream!"}}' | $APS_BIN run --stream "$EXAMPLE" || true
fi

echo
echo "[SUCCESS] test-release finished. Temp artifacts at: $TMPROOT"

