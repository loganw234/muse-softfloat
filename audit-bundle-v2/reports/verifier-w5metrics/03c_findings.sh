#!/usr/bin/env bash
# Probe 3C: dump findings headers of remaining verifier reports.
set -euo pipefail
ulimit -v 1048576 2>/dev/null || true
cd "C:/Users/logan/source/repos/Muse-Softfloat"
for d in verifier-w4trig verifier-w4kissfft verifier-w5attr verifier-readme2 verifier-w5alg1 verifier-w5alg2 verifier-w5site verifier-w5demo verifier-w5exp2 verifier-w5twiddledoc verifier-w5log2 verifier-w5aug; do
  echo "############ $d"
  grep -nE '^#{1,4} .*|^- \*\*[A-Z][0-9]' "scratch/$d/report.md" 2>/dev/null | head -25 || echo "(no report)"
done
