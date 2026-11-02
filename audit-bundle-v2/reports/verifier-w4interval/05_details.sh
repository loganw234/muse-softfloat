#!/usr/bin/env bash
# 05_details.sh - host rows for id 2 and id 6; source scans over the copy.
set -u
VROOT="/c/Users/logan/source/repos/Muse-Softfloat"
COPY="$VROOT/worktrees/verify4-interval"
OUT="$VROOT/scratch/verifier-w4interval/build"
echo "--- host rows id 2 and id 6 ---"
grep -E "^RAY id=(2|6) " "$OUT/host_out.txt"
echo "--- _number scan: core + host main ---"
grep -rn "_number" "$COPY/board/interval_workload.c" "$COPY/board/interval_workload.h" "$COPY/board/interval_host.c" || echo "no _number (exit $?)"
echo "--- hardware float words in core ---"
grep -rnwE "float|double" "$COPY/board/interval_workload.c" "$COPY/board/interval_workload.h" || echo "no float/double words"
echo "--- allocation words in core ---"
grep -rnwE "malloc|calloc|realloc|free" "$COPY/board/interval_workload.c" "$COPY/board/interval_workload.h" || echo "no allocation words"
echo "--- IW_RM_LO / IW_STAGE3_GUARD references in copy (excl .git) ---"
grep -rn "IW_RM_LO\|IW_STAGE3_GUARD" "$COPY/board" "$COPY/tests" "$COPY/tools" 2>/dev/null
echo "--- minimum/maximum call inventory in core ---"
grep -rno "msf[0-9]*_minimum[a-z_]*\|msf[0-9]*_maximum[a-z_]*" "$COPY/board/interval_workload.c"
