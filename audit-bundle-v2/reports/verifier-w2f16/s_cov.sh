#!/usr/bin/env bash
# s_cov.sh - enumerate wave-2 f16 rows by authority from the copy
set -u
CP="C:/Users/logan/source/repos/Muse-Softfloat/worktrees/verify2-f16"
SC="C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w2f16"
cd "$CP" || exit 9
head -1 docs/COVERAGE.tsv
awk -F'\t' '$1 ~ /^msf16_/ && $2==2' docs/COVERAGE.tsv | wc -l
echo "=== by authority ==="
awk -F'\t' '$1 ~ /^msf16_/ && $2==2 {print $NF}' docs/COVERAGE.tsv | sort | uniq -c
echo "=== berkeley rows ==="
awk -F'\t' '$1 ~ /^msf16_/ && $2==2 && ($NF=="berkeley" || $NF=="project-exact+berkeley-check") {print $1, $NF}' docs/COVERAGE.tsv
