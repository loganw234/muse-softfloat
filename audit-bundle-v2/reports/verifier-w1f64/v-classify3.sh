#!/usr/bin/env bash
set -uo pipefail
cd /c/Users/logan/source/repos/Muse-Softfloat
LOG=scratch/verifier-w1f64/v-exact-run.log
echo "=== the 1 nonconforming div FAIL: ==="
grep "^FAIL" "$LOG" | grep -E "w164-arith" | grep "msf64_div" | grep -vE "got [0-9a-f]+/00 want [0-9a-f]+/02"
echo "=== sample of arith-prov div FAILs: ==="
grep "^FAIL" "$LOG" | grep -E "w164-arith" | grep "msf64_div" | head -n 6
echo "=== count arith-prov div FAILs: ==="
grep "^FAIL" "$LOG" | grep -E "w164-arith" | grep -c "msf64_div"
