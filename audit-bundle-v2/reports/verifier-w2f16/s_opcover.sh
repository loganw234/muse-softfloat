#!/usr/bin/env bash
# s_opcover.sh - check every wave-2 msf16 op appears in committed vectors
set -u
cd "C:/Users/logan/source/repos/Muse-Softfloat/worktrees/verify2-f16" || exit 9
grep -v '^#' docs/COVERAGE.tsv | awk -F'\t' '$1 ~ /^msf16_/ && $8==2 {print $1}' | sort -u > /tmp/allops.txt
cat tests/vectors/*f16*.vec | grep -v '^#' | awk '{print $1}' | sort -u > /tmp/vecops.txt
wc -l /tmp/allops.txt /tmp/vecops.txt
echo "=== ops with NO committed vector ==="
comm -23 /tmp/allops.txt /tmp/vecops.txt
echo "=== from_f NaN expectations in committed vectors ==="
grep -h 'from_f' tests/vectors/*.vec | grep -iE '7c|7e|fc|fe|7d|fd' | head -12
echo "=== standard.log verify-standard section ==="
grep -E '^(file|prov|total|VERDICT|budget)' "C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w2f16/standard.log" | head -20
