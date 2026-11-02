#!/usr/bin/env bash
# Probe 3B: grep each appended verifier's report for its own (a)/(b) tally.
set -euo pipefail
ulimit -v 1048576 2>/dev/null || true
cd "C:/Users/logan/source/repos/Muse-Softfloat"
for d in verifier-readme verifier-sf2 verifier-w4seam verifier-w4trig verifier-w4kissfft verifier-w5attr verifier-readme2 verifier-w5alg1 verifier-w5alg2 verifier-w5site verifier-w5demo verifier-w5exp2 verifier-w5twiddledoc verifier-w5log2 verifier-w5aug verifier-w4minmax verifier-w4interval; do
  echo "== $d"
  grep -ohE '\(a\)[^.]{0,80}|\(b\)[^.]{0,80}' "scratch/$d/report.md" 2>/dev/null | head -8 || echo "(no report or no match)"
done
