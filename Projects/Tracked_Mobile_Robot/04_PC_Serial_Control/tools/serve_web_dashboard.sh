#!/usr/bin/env bash
set -euo pipefail

PORT="${1:-8765}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/web_serial_dashboard"

cd "$ROOT"

if command -v python3 >/dev/null 2>&1; then
    echo "Serving $ROOT"
    echo "Open http://localhost:$PORT/"
    python3 -m http.server "$PORT" --bind 127.0.0.1
elif command -v busybox >/dev/null 2>&1; then
    echo "Serving $ROOT"
    echo "Open http://localhost:$PORT/"
    busybox httpd -f -p "127.0.0.1:$PORT"
else
    echo "python3 or busybox is required to serve the dashboard" >&2
    exit 1
fi
