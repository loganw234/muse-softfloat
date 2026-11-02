#!/usr/bin/env bash
# 46_triage.sh - categorize vec diffs (all lines, no cap).
set -u
D="$(dirname "$0")"
{
for f in f16 f32 f64; do
  echo "=== $f ==="
  echo "undecided: $(grep -c VEC-UNDECIDED "$D/45_explog-$f.log")"
  echo "value diffs: $(grep -c 'VEC-DIFF ' "$D/45_explog-$f.log")"
  echo "--- by op+mode (value diffs) ---"
  grep 'VEC-DIFF ' "$D/45_explog-$f.log" | awk '{print $2, $3}' | sort | uniq -c | sort -rn | head -12
  echo "--- first 8 value diffs ---"
  grep 'VEC-DIFF ' "$D/45_explog-$f.log" | head -8
  echo "--- first 5 undecided ---"
  grep VEC-UNDECIDED "$D/45_explog-$f.log" | head -5
done
} 2>&1 | tee "$D/46_triage.log"
