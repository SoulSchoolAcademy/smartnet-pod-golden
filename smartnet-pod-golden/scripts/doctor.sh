#!/usr/bin/env bash
set -e
echo "=== SmartNET Doctor ==="
echo -n "Node: " && node -v
echo -n "npm: " && npm -v
echo -n "pnpm: " && pnpm -v
echo -n "git: " && git --version
echo -n "code-server: " && /opt/code-server/bin/code-server --version
