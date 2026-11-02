#!/usr/bin/env bash
# s_unary.sh - enumerate unary f16->f16 wave-2 rows
set -u
cd "C:/Users/logan/source/repos/Muse-Softfloat/worktrees/verify2-f16" || exit 9
grep -v '^#' docs/COVERAGE.tsv | awk -F'\t' '$1 ~ /^msf16_/ && $8==2 && $4=="f16" && $5=="f16" {print $1, $10, $11}'
