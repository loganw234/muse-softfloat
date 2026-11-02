#!/usr/bin/env bash
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
export TMPDIR="$HERE/tmp"
mkdir -p "$TMPDIR"
BASE="/c/Users/logan/.local/share/muse/sessions/2026/10/26/01a17907-4147-7333-a565-56071da9d971/subagent"
python "$HERE/dup_check.py" \
  "$BASE/01a17910-9a6b-75a0-8c0b-2dff80999219/session.jsonl" \
  "$BASE/097760c4-44fd-7396-8050-2f11f128ddae/session.jsonl"
