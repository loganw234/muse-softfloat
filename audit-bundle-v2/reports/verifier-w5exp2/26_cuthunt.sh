#!/usr/bin/env bash
# 26_cuthunt.sh - find committed-vector lines for the tie cells.
set -u
D="$(dirname "$0")"
ROOT="$(cd "$D/../.." && pwd)"
COPY="$ROOT/worktrees/verify5-exp2"
{
echo "--- f64 -1075 (c090cc0000000000) ---"
grep -h "c090cc0000000000" "$COPY/tests/vectors/explog-f64.vec" | head -8
echo "--- f32 -150 (c3160000) ---"
grep -h "c3160000" "$COPY/tests/vectors/explog-f32.vec" | head -8
echo "--- f16 -25 (ce40) ---"
grep -h "ce40" "$COPY/tests/vectors/explog-f16.vec" | head -8
echo "--- vec line format head ---"
head -3 "$COPY/tests/vectors/explog-f64.vec"
grep -n "ta\b" "$COPY/tests/VECTORS.md" | head -10
} 2>&1 | tee "$D/26_cuthunt.log"
