#!/usr/bin/env bash
# s_subchar.sh - characterize f16_sub level-1 failures
set -u
SC="C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w2f16"
CP="C:/Users/logan/source/repos/Muse-Softfloat/worktrees/verify2-f16"
cd "$CP" || exit 9
R="build/smoke/msf_runner.exe"
"$R" verify "$SC/berk1/f16_sub-te-l1.vec" > "$SC/sub-te-full.log" 2>&1
grep -E '^FAIL' "$SC/sub-te-full.log" | sed -E 's/^[^|]*\| //' | sort | uniq -c | sort -rn | head -20 > "$SC/sub-patterns.txt"
cat "$SC/sub-patterns.txt"
echo "=== sample non-inf fails ==="
grep -E '^FAIL' "$SC/sub-te-full.log" | grep -vE '7c00|fc00' | head -10
echo "=== div: confirm all fails are x2 (result exponent+1)? sample ==="
"$R" verify "$SC/berk1/f16_div-te-l1.vec" > "$SC/div-te-full.log" 2>&1
grep -E '^FAIL' "$SC/div-te-full.log" | head -5
grep -cE '^FAIL' "$SC/div-te-full.log"
