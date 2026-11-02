#!/usr/bin/env bash
# 13_surface.sh - claim-surface, provenance, allocation-call and host scans.
set -u
VROOT="/c/Users/logan/source/repos/Muse-Softfloat"
COPY="$VROOT/worktrees/verify4-interval"
export MSF_PYTHON="/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe"
echo "--- diff parent..HEAD (claim surface) ---"
git -C "$COPY" diff --name-only b704b4c HEAD
echo "--- copy status ---"
git -C "$COPY" status --short; echo "(clean above)"
echo "--- hand-written line counts ---"
wc -l "$COPY/board/interval_workload.c" "$COPY/board/interval_workload.h" \
  "$COPY/board/interval_host.c" "$COPY/tests/gen_interval_catalogue.py"
echo "--- metrics row for this parcel ---"
grep "parcel-w4interval" "$COPY/docs/metrics/briefs.jsonl" | cut -c1-400
echo "--- allocation CALLS in core (parens => real calls) ---"
grep -rnE "(malloc|calloc|realloc|free)[[:space:]]*\(" \
  "$COPY/board/interval_workload.c" "$COPY/board/interval_workload.h" \
  || echo "no allocation calls"
echo "--- hardware float words in host main ---"
grep -rnwE "float|double" "$COPY/board/interval_host.c" || echo "host main: no float/double words"
echo "--- _number in host main ---"
grep -rn "_number" "$COPY/board/interval_host.c" || echo "host main: no _number"
echo "--- catalogue provenance/ids ---"
"$MSF_PYTHON" "C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w4interval/13_prov.py"
