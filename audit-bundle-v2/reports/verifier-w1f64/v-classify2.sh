#!/usr/bin/env bash
# verifier-w164: strict check - every non-div arith FAIL is (+-0,+-0) tp/tn.
set -uo pipefail
cd /c/Users/logan/source/repos/Muse-Softfloat
LOG=scratch/verifier-w1f64/v-exact-run.log
TMPF=$(mktemp)
grep "^FAIL" "$LOG" | grep "w164-arith" | grep -v "msf64_div" | sed 's/.*| //' > "$TMPF"
echo "nonddiv-arith-fails: $(wc -l < "$TMPF")"
echo "all-signed-zero-tp-tn: $(grep -cE 'msf64_(add|sub)[^ ]* t[pn] (0|8000000000000000|80000000) (0|8000000000000000|80000000) ->' "$TMPF")"
echo "--- any other shape: ---"
grep -vE 'msf64_(add|sub)[^ ]* t[pn] (0|8000000000000000|80000000) (0|8000000000000000|80000000) ->' "$TMPF" | head
echo "=== div0/div FAILs all got-00-want-02 (printed: nonconforming count): ==="
grep "^FAIL" "$LOG" | grep -E "w164-arith" | grep "msf64_div" | grep -vcE "got [0-9a-f]+/00 want [0-9a-f]+/02"
echo "=== fma-special: inf-rule (96) + zerozero-tp-tn (16)? ==="
grep "^FAIL" "$LOG" | grep "fma-special" | wc -l
rm -f "$TMPF"
