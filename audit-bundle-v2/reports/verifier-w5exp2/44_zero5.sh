#!/usr/bin/env bash
# 44_zero5.sh - show all 5 mode lines for input 0, both functions, all formats.
set -u
D="$(dirname "$0")"
ROOT="$(cd "$D/../.." && pwd)"
COPY="$ROOT/worktrees/verify5-exp2"
{
for pat in "msf64_exp2" "msf64_exp2m1" "msf32_exp2" "msf32_exp2m1" "msf16_exp2" "msf16_exp2m1"; do
  echo "--- $pat input 0 ---"
  grep -F "$pat te 0 " "$COPY/tests/vectors/explog-f64.vec" "$COPY/tests/vectors/explog-f32.vec" "$COPY/tests/vectors/explog-f16.vec" 2>/dev/null | head -3
  grep -F "$pat ta 0 " "$COPY/tests/vectors/explog-f64.vec" "$COPY/tests/vectors/explog-f32.vec" "$COPY/tests/vectors/explog-f16.vec" 2>/dev/null | head -3
done
} 2>&1 | tee "$D/44_zero5.log"
