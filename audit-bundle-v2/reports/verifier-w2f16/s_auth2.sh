#!/usr/bin/env bash
# s_auth2.sh - authority distribution of div/sub rows
set -u
cd "C:/Users/logan/source/repos/Muse-Softfloat/worktrees/verify2-f16" || exit 9
echo "--- div authorities:"
grep -v '^#' docs/COVERAGE.tsv | awk -F'\t' '$1 ~ /^msf16_div/ && $8==2 {print $10}' | sort | uniq -c
echo "--- sub authorities:"
grep -v '^#' docs/COVERAGE.tsv | awk -F'\t' '$1 ~ /^msf16_sub/ && $8==2 {print $10}' | sort | uniq -c
echo "--- add/mul authorities:"
grep -v '^#' docs/COVERAGE.tsv | awk -F'\t' '$1 ~ /^msf16_(add|mul)/ && $8==2 {print $10}' | sort | uniq -c
