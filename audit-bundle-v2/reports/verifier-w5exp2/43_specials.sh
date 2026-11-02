#!/usr/bin/env bash
# 43_specials.sh - runner-verify the specials lines the vectors claim.
set -u
D="$(dirname "$0")"
ROOT="$(cd "$D/../.." && pwd)"
COPY="$ROOT/worktrees/verify5-exp2"
OUT="$D/build"
grep -F "mpfr-explog:specials" "$COPY/tests/vectors/explog-f64.vec" > "$OUT/specials-f64.vec"
wc -l "$OUT/specials-f64.vec"
"$OUT/msf_runner.exe" verify "$OUT/specials-f64.vec" 2>&1 | tail -12 | tee "$D/43_specials.log"
