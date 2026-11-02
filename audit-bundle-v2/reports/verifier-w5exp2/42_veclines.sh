#!/usr/bin/env bash
# 42_veclines.sh - inspect specials lines in committed vectors + generator.
set -u
D="$(dirname "$0")"
ROOT="$(cd "$D/../.." && pwd)"
COPY="$ROOT/worktrees/verify5-exp2"
{
echo "--- f64 specials lines (input 0,1) ---"
grep -F "msf64_exp2 te 0 " "$COPY/tests/vectors/explog-f64.vec" | head -4
grep -F "msf64_exp2 te 1 " "$COPY/tests/vectors/explog-f64.vec" | head -6
grep -F "msf64_exp2m1 te 0 " "$COPY/tests/vectors/explog-f64.vec" | head -4
echo "--- generator specials handling ---"
grep -n "special" "$COPY/tests/gen_vectors_explog.py" | head -20
} 2>&1 | tee "$D/42_veclines.log"
