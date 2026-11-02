#!/usr/bin/env bash
R=/c/Users/logan/source/repos/Muse-Softfloat
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
cd "$R/scratch/verifier-w3str" || exit 9
echo "=== malformed lines:"
grep -n '^MALFORMED\|malformed' adv.log | head -30
grep '^FAIL\|^MAL' adv.log | head -5
echo "=== fail by file:"
grep '^FAIL' adv.log | cut -d: -f1 | sort | uniq -c
echo "=== sample FAILs:"
grep '^FAIL' adv.log | head -20
