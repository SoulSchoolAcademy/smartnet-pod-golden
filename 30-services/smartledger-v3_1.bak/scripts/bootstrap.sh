#!/usr/bin/env bash
set -euo pipefail
: "${DATABASE_URL:?set DATABASE_URL first}"
psql "$DATABASE_URL" -f sql/schema.sql
echo "DB ready."
