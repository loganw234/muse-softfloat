#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify-f32 || exit 9
echo "=== wave1 msf32 rows by authority ==="
awk -F'\t' '$8==1 && $1 ~ /^msf32_/ {print $10}' docs/COVERAGE.tsv | sort | uniq -c
echo "=== berkeley-authority wave1 msf32 names ==="
awk -F'\t' '$8==1 && $1 ~ /^msf32_/ && $10=="berkeley" {print $1}' docs/COVERAGE.tsv
echo "=== non-berkeley wave1 msf32 names ==="
awk -F'\t' '$8==1 && $1 ~ /^msf32_/ && $10!="berkeley" {print $1, $10}' docs/COVERAGE.tsv
