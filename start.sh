#!/usr/bin/env bash
# AI_ASSIST_JD — platform startup script
# Usage: ./start.sh
# Opens:  http://localhost:5001  (hub + JD Generator)
#         http://localhost:5173  (AI Voice Screening)

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
kill_port 5002
kill_port 5001
kill_port 5173

# ── start JD Prototype (Flask) ───────────────────────────────────────────────
echo "→ Starting JD Generator (Flask) on port 5001..."
cd "$ROOT/jd_prototype"
# Use --no-reload to avoid the reloader child-process holding the port on restart
FLASK_ENV=development python3 -c "
import os, sys
sys.path.insert(0, '.')
from dotenv import load_dotenv
load_dotenv()
from app import app
port = int(os.getenv('PORT', 5001))
app.run(debug=True, port=port, use_reloader=False)
" > "$ROOT/logs/flask.log" 2>&1 &
FLASK_PID=$!
echo "  Flask PID: $FLASK_PID"

# ── start Darwinbox (Flask) ──────────────────────────────────────────────────
echo "→ Starting Darwinbox HRIS (Flask) on port 5002..."
cd "$ROOT/DummyDarwin-main"
python3 app.py > "$ROOT/logs/darwin.log" 2>&1 &
DARWIN_PID=$!
echo "  Darwin PID: $DARWIN_PID"

# ── start VoiceAgent (Vite) ──────────────────────────────────────────────────
echo "→ Starting AI Voice Screening (Vite) on port 5173..."
cd "$ROOT/VoiceAgent"
npm run dev > "$ROOT/logs/vite.log" 2>&1 &
VITE_PID=$!
echo "  Vite PID: $VITE_PID"

# ── wait for Flask to be ready ───────────────────────────────────────────────
echo "→ Waiting for Flask..."
for i in $(seq 1 20); do
  if curl -s http://localhost:5001/hub > /dev/null 2>&1; then
    echo "  ✓ Flask ready"
    break
  fi
  sleep 0.5
done

# ── done ─────────────────────────────────────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Platform Hub      → http://localhost:5001"
echo "  JD Generator      → http://localhost:5001/library"
echo "  AI Voice Agent    → http://localhost:5173"
echo "  Darwinbox HRIS    → http://localhost:5002"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Logs: $ROOT/logs/flask.log"
echo "        $ROOT/logs/vite.log"
echo "        $ROOT/logs/darwin.log"
echo ""
echo "  Press Ctrl+C to stop all servers"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# keep script alive so Ctrl+C stops both
trap "echo ''; echo 'Stopping...'; kill $FLASK_PID $DARWIN_PID $VITE_PID 2>/dev/null; exit 0" INT TERM
wait
