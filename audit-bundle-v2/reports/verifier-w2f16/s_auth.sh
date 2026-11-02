#!/usr/bin/env bash
# s_auth.sh - authority of div/sub rows
set -u
cd "C:/Users/logan/source/repos/Muse-Softfloat/worktrees/verify2-f16" || exit 9
grep -v '^#' docs/COVERAGE.tsv | awk -F'\t' '$1 ~ /^msf16_(div|sub)/ && $8==2 {print $1, $10}' | sed 's/msf16_div.*/DIV/;s/msf16_sub.*/SUB/' | sort | uniq -c
