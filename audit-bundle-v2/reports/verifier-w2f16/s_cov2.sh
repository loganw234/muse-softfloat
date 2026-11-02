#!/usr/bin/env bash
# s_cov2.sh - enumerate wave-2 msf16 rows by authority (skip # header)
set -u
CP="C:/Users/logan/source/repos/Muse-Softfloat/worktrees/verify2-f16"
cd "$CP" || exit 9
echo "=== wave-2 msf16 count ==="
grep -v '^#' docs/COVERAGE.tsv | awk -F'\t' '$1 ~ /^msf16_/ && $8==2' | wc -l
echo "=== by authority ==="
grep -v '^#' docs/COVERAGE.tsv | awk -F'\t' '$1 ~ /^msf16_/ && $8==2 {print $10}' | sort | uniq -c
echo "=== berkeley + berkeley-check rows ==="
grep -v '^#' docs/COVERAGE.tsv | awk -F'\t' '$1 ~ /^msf16_/ && $8==2 && ($10=="berkeley" || $10=="project-exact+berkeley-check") {print $1, $10, $11, $12}'
