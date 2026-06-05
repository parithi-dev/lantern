#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

echo "Starting NetPulse..."
echo "  Dashboard: http://localhost:8000"
echo ""

exec sudo "${ROOT}/agent/.venv/bin/python" -m agent.run
