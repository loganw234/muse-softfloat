#!/usr/bin/env bash
# Watch each named mutant refusing the committed aug vectors.
set -u
source "$(dirname "$0")/env.sh"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
SRC="src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c src/msf_string.c src/msf_math.c src/msf_alg.c src/msf_aug.c"
OUT="$WS/scratch/parcel-w5aug/logs/mutants"
mkdir -p "$OUT" build/aug-mut
VECS="tests/vectors/aug-f16.vec tests/vectors/aug-f32.vec tests/vectors/aug-f64.vec"
SUMMARY="$OUT/summary.txt"
: > "$SUMMARY"
failall=0
run_one() {
  local name="$1" def="$2"
  local exe="build/aug-mut/runner-$name.exe"
  if [ -n "$def" ]; then
    gcc -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off -D"$def" $SRC tests/runner.c tests/sha256.c -o "$exe" > "$OUT/build-$name.log" 2>&1
  else
    gcc -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off $SRC tests/runner.c tests/sha256.c -o "$exe" > "$OUT/build-$name.log" 2>&1
  fi
  if [ $? -ne 0 ]; then
    echo "$name BUILD-FAILED" >> "$SUMMARY"; cat "$OUT/build-$name.log"; failall=1; return
  fi
  "$exe" verify $VECS > "$OUT/verify-$name.log" 2>&1
  local rc=$?
  local nfail
  nfail=$(grep -c '^FAIL' "$OUT/verify-$name.log" || true)
  local verdict
  verdict=$(grep '^VERDICT' "$OUT/verify-$name.log" || echo "no-verdict")
  echo "$name def=${def:-none} rc=$rc fail_lines=$nfail $verdict" >> "$SUMMARY"
  grep '^FAIL' "$OUT/verify-$name.log" | head -3 >> "$SUMMARY" || true
  if [ -n "$def" ]; then
    if [ $rc -eq 0 ] || [ "$nfail" = "0" ]; then
      echo "$name NOT-REFUSED" >> "$SUMMARY"; failall=1
    fi
  else
    if [ $rc -ne 0 ]; then
      echo "control build FAILED the vectors" >> "$SUMMARY"; failall=1
    fi
  fi
}
run_one control ""
run_one te-head MSF_AUG_TEST_TE_HEAD
run_one zero-tail-sign MSF_AUG_TEST_ZERO_TAIL_SIGN
run_one swap-pair MSF_AUG_TEST_SWAP_PAIR
run_one jam-window MSF_AUG_TEST_JAM_WINDOW
run_one p1-opposite MSF_AUG_TEST_P1_OPPOSITE
run_one pack-leak MSF_AUG_TEST_PACK_LEAK
# Corrupted pair expectation: flip one expected tail bit and
# require the shipped runner to refuse it.
"$MSF_PYTHON" "$WS/scratch/parcel-w5aug/scripts/corrupt_pair.py" \
  tests/vectors/aug-f64.vec "$OUT/corrupt-pair.vec" >> "$SUMMARY" 2>&1
build/aug-mut/runner-control.exe verify "$OUT/corrupt-pair.vec" > "$OUT/verify-corrupt.log" 2>&1
rc=$?
echo "corrupt-pair rc=$rc $(grep '^VERDICT' "$OUT/verify-corrupt.log" || true)" >> "$SUMMARY"
if [ $rc -eq 0 ]; then echo "corrupt-pair NOT-REFUSED" >> "$SUMMARY"; failall=1; fi
cat "$SUMMARY"
exit $failall
