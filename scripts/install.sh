#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "========================================"
echo "  NetPulse — One-time Install"
echo "========================================"
echo ""

# --- Python agent ---
echo "[1/3] Setting up Python agent..."
python3 -m venv agent/.venv
source agent/.venv/bin/activate
pip install -q -r agent/requirements.txt
echo "      Done."

# --- Frontend ---
echo "[2/3] Installing frontend dependencies..."
npm ci --silent
echo "      Done."

echo "[3/3] Building frontend..."
npx ng build --silent
echo "      Done."

echo ""
echo "========================================"
echo "  NetPulse is ready!"
echo "========================================"
echo ""
echo "  Start the server:"
echo "    sudo agent/.venv/bin/python -m agent.run"
echo ""
echo "  Open in browser:"
echo "    http://localhost:8000"
echo ""
echo "  (sudo is needed for network scanning."
echo "   If you skip sudo, some features may be limited.)"
echo ""
