#!/usr/bin/env bash
# verifier-w164: classify residual exact-probe FAILs.
set -uo pipefail
cd /c/Users/logan/source/repos/Muse-Softfloat
LOG=scratch/verifier-w1f64/v-exact-run.log
echo "=== arith FAIL operand classes ==="
grep "^FAIL" "$LOG" | grep "w164-arith" | grep -v "msf64_div" | \
  sed 's/.*| //' | awk '{print $1, $3, $4}' | sort | uniq -c | sort -rn | head -n 20
echo "=== arith FAIL: any nonzero operand? ==="
grep "^FAIL" "$LOG" | grep "w164-arith" | grep -v "msf64_div" | \
  grep -vE "(msf64_(add|sub)[^ ]* (te|tz|tp|tn) (0|8000000000000000) (0|8000000000000000) ->)" | head -n 10
echo "=== div FAIL: all div0 (want 02, got 00)? ==="
grep "^FAIL" "$LOG" | grep -E "exact-w164:div0? " | grep -vc "got [0-9a-f]*/00 want [0-9a-f]*/02"
echo "=== fma-special FAIL classes ==="
grep "^FAIL" "$LOG" | grep "fma-special" | sed 's/.*| //' | awk '{print $4, $5, $6}' | sort | uniq -c | sort -rn | head -n 20
