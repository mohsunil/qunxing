#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")/.."
if command -v python3 >/dev/null 2>&1; then
  python3 scripts/validate_handoff.py
elif command -v python >/dev/null 2>&1; then
  python scripts/validate_handoff.py
else
  echo "Python 3 is required for handoff validation." >&2
  exit 1
fi
echo "Design handoff validated. No playable Stellaris build or in-game test was performed."

