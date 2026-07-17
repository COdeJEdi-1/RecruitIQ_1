#!/usr/bin/env bash
# AI_ASSIST_JD — platform startup script
# Usage: ./start.sh
# Opens:  http://localhost:6001  (hub + JD Generator)
#         http://localhost:6004  (AI Voice Screening)

set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"

# ── helpers ──────────────────────────────────────────────────────────────────
kill_port() {
  local pids
  pids=$(lsof -ti :"$1" 2>/dev/null) || true
  if [ -n "$pids" ]; then
    echo "  Clearing port $1 (pids: $pids)"
    echo "$pids" | xargs kill -9 2>/dev/null || true
    sleep 0.5
  fi
}

# ── clear ports ──────────────────────────────────────────────────────────────
echo "→ Clearing ports..."
kill_port 6002
kill_port 6001
kill_port 6004
kill_port 6003

# ── start JD Prototype (Flask) ───────────────────────────────────────────────
echo "→ Starting JD Generator (Flask) on port 6001..."
cd "$ROOT/jd_prototype"
python3 app.py > "$ROOT/logs/flask.log" 2>&1 &
FLASK_PID=$!
echo "  Flask PID: $FLASK_PID"

# ── start Darwinbox (Flask) ──────────────────────────────────────────────────
echo "→ Starting Darwinbox HRIS (Flask) on port 6002..."
cd "$ROOT/DummyDarwin-main"
python3 app.py > "$ROOT/logs/darwin.log" 2>&1 &
DARWIN_PID=$!
echo "  Darwin PID: $DARWIN_PID"

# ── start AI_VoiceAgent webhook server (Node) ────────────────────────────────
echo "→ Starting AI_VoiceAgent Webhook Server on port 6003..."
cd "$ROOT/AI_VoiceAgent"
npm run dev:webhook > "$ROOT/logs/webhook.log" 2>&1 &
WEBHOOK_PID=$!
echo "  Webhook PID: $WEBHOOK_PID"

# ── start AI_VoiceAgent (Vite) ────────────────────────────────────────────────
echo "→ Starting AI Voice Screening (Vite) on port 6004..."
cd "$ROOT/AI_VoiceAgent"
npm run dev -- --port 6004 > "$ROOT/logs/vite.log" 2>&1 &
VITE_PID=$!
echo "  Vite PID: $VITE_PID"

# ── wait for Flask to be ready ───────────────────────────────────────────────
echo "→ Waiting for Flask..."
for i in $(seq 1 20); do
  if curl -s http://localhost:6001/hub > /dev/null 2>&1; then
    echo "  ✓ Flask ready"
    break
  fi
  sleep 0.5
done

# ── done ─────────────────────────────────────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Platform Hub      → http://localhost:6001"
echo "  JD Generator      → http://localhost:6001/library"
echo "  AI Voice Agent    → http://localhost:6004"
echo "  Voice Webhook     → http://localhost:6003"
echo "  Darwinbox HRIS    → http://localhost:6002"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Logs: $ROOT/logs/flask.log"
echo "        $ROOT/logs/vite.log"
echo "        $ROOT/logs/webhook.log"
echo "        $ROOT/logs/darwin.log"
echo ""
echo "  Press Ctrl+C to stop all servers"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# keep script alive so Ctrl+C stops all four
trap "echo ''; echo 'Stopping...'; kill $FLASK_PID $DARWIN_PID $WEBHOOK_PID $VITE_PID 2>/dev/null; exit 0" INT TERM
wait
