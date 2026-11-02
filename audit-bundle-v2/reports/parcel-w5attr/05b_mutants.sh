#!/usr/bin/env bash
set -u
WS=/c/Users/logan/source/repos/Muse-Softfloat
cd "$WS/worktrees/w5-attr" || exit 9
S="$WS/scratch/parcel-w5attr"
export TMPDIR="$S/tmp"
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-w5attr\tmp'
export TEMP="$TMP"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
SRC="src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c src/msf_math.c"
for m in dec hex; do
  gcc -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off -Isrc -Iinclude \
    -DMSF_BUILD_ID="\"mutant-$m\"" \
    $SRC "$S/out/ctrl/msf_string_mutant_$m.c" tests/runner.c tests/sha256.c \
    -o "$S/out/ctrl/runner_mutant_$m.exe" > "$S/out/ctrl/build_$m.log" 2>&1
  echo "mutant-$m build rc=$?"; cat "$S/out/ctrl/build_$m.log"
done
echo "===== control (a) dec mutant on dec files (must FAIL) ====="
"$S/out/ctrl/runner_mutant_dec.exe" verify tests/vectors/to-decimal-str.vec tests/vectors/from-decimal-str.vec > "$S/out/ctrl/verify_mutant_dec.log" 2>&1
echo "verify rc=$? (nonzero required)"
grep -E '^(total|VERDICT)' "$S/out/ctrl/verify_mutant_dec.log"
grep -m3 '^FAIL' "$S/out/ctrl/verify_mutant_dec.log" || true
echo "===== control (a) dec mutant on non-dec files (sanity PASS) ====="
"$S/out/ctrl/runner_mutant_dec.exe" verify tests/vectors/to-hex-str.vec tests/vectors/arith-f32.vec > "$S/out/ctrl/verify_mutant_dec_sanity.log" 2>&1
echo "verify rc=$? (zero required)"
grep -E '^(total|VERDICT)' "$S/out/ctrl/verify_mutant_dec_sanity.log"
echo "===== control (a2) hex mutant on to-hex (must FAIL) ====="
"$S/out/ctrl/runner_mutant_hex.exe" verify tests/vectors/to-hex-str.vec > "$S/out/ctrl/verify_mutant_hex.log" 2>&1
echo "verify rc=$? (nonzero required)"
grep -E '^(total|VERDICT)' "$S/out/ctrl/verify_mutant_hex.log"
grep -m3 '^FAIL' "$S/out/ctrl/verify_mutant_hex.log" || true
echo "===== control (a2) hex mutant sanity on dec files (PASS) ====="
"$S/out/ctrl/runner_mutant_hex.exe" verify tests/vectors/to-decimal-str.vec tests/vectors/from-decimal-str.vec > "$S/out/ctrl/verify_mutant_hex_sanity.log" 2>&1
echo "verify rc=$? (zero required)"
grep -E '^(total|VERDICT)' "$S/out/ctrl/verify_mutant_hex_sanity.log"
