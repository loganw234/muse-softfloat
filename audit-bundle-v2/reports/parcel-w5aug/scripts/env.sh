#!/usr/bin/env bash
# Shared env for parcel-w5aug scripts. Source from Git Bash.
WS="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
REPO="$WS/worktrees/w5-aug"
export MSF_PYTHON="$WS/.venv/Scripts/python.exe"
mkdir -p "$WS/scratch/parcel-w5aug/tmp" "$WS/scratch/parcel-w5aug/logs"
export TMPDIR="$WS/scratch/parcel-w5aug/tmp"
export TMP="$(cygpath -w "$TMPDIR" 2>/dev/null || echo "$TMPDIR")"
export TEMP="$TMP"
cd "$REPO" || exit 9
