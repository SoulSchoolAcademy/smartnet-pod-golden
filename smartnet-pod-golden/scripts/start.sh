#!/usr/bin/env bash
set -euo pipefail

PORT="${CS_PORT:-8080}"
PASS="${CODE_SERVER_PASSWORD:-SmartNet!2025}"
WS="${WORKSPACE_DIR:-/workspace}"

mkdir -p "$WS"

echo "🔑 code-server password: $PASS"
echo "🌐 code-server listening on 0.0.0.0:${PORT}"
echo "📁 workspace: $WS"

exec /opt/code-server/bin/code-server       --bind-addr 0.0.0.0:"$PORT"       --auth password       --password "$PASS"       "$WS"
