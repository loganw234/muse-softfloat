#!/bin/bash
# Probe 1b: locate the non-prefix difference in usage.jsonl.
set -u
DUP="C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w6metrics/dup"
OUT="C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w6metrics/out"
cd "$DUP"
head -n 93 docs/metrics/usage.jsonl > "$OUT/tip-usage-head93.jsonl"
diff "$OUT/parent-usage.jsonl" "$OUT/tip-usage-head93.jsonl" | head -20
echo "=== diff line count above ==="
diff "$OUT/parent-usage.jsonl" "$OUT/tip-usage-head93.jsonl" | wc -l
echo "=== git diff of usage, first 60 lines ==="
git diff cdc40ae HEAD -- docs/metrics/usage.jsonl | head -60
