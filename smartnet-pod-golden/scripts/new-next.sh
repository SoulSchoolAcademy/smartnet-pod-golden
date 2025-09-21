#!/usr/bin/env bash
# Usage: new-next [app_name] [next_version]
set -euo pipefail
APP="${1:-smartnet-web}"
VER="${2:-15.1.6}"
mkdir -p "/workspace/${APP}"
cd "/workspace/${APP}"
pnpm dlx create-next-app@"${VER}" . --ts --app --tailwind --src-dir --eslint --use-pnpm --yes
echo "Run: cd /workspace/${APP} && pnpm dev --port 3000"
