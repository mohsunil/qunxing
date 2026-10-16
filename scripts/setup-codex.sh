#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")/.."
if command -v python3 >/dev/null 2>&1; then
  python3 scripts/validate_handoff.py
  python3 scripts/validate_mod.py
elif command -v python >/dev/null 2>&1; then
  python scripts/validate_handoff.py
  python scripts/validate_mod.py
else
  echo "Python 3 is required for handoff validation." >&2
  exit 1
fi
echo "Requirements, archive integrity and population algorithm checked. Engine loading and in-game behavior remain unverified."

