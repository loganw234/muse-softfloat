#!/usr/bin/env bash
# 05_controls.sh - brief negative controls, watched refused;
# JAM build watched with expected PASS (equivalence addendum).
set -u
ulimit -v 2097152 || echo "ulimit -v unsupported here (recorded)"
WS=/c/Users/logan/source/repos/Muse-Softfloat
cd "$WS/worktrees/w5-alg2" || exit 9
S="$WS/scratch/parcel-w5alg2"
mkdir -p "$S/out/ctrl" "$S/tmp"
export TMPDIR="$S/tmp"
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-w5alg2\tmp'
export TEMP="$TMP"
export MSF_PYTHON="$WS/.venv/Scripts/python.exe"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
PY="$MSF_PYTHON"
SRC="src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c src/msf_string.c src/msf_math.c src/msf_alg.c"
CFLAGS="-std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off"

echo "===== build runners (normal, jam, nosticky) on final tree ====="
gcc $CFLAGS -DMSF_BUILD_ID='"ctrl2"' $SRC tests/runner.c tests/sha256.c \
  -o "$S/out/ctrl/runner.exe" > "$S/out/ctrl/build.log" 2>&1; echo "normal rc=$?"
gcc $CFLAGS -DMSF_BUILD_ID='"ctrl2-jam"' -DMSF_ALG_TEST_JAM $SRC tests/runner.c tests/sha256.c \
  -o "$S/out/ctrl/runner_jam.exe" >> "$S/out/ctrl/build.log" 2>&1; echo "jam rc=$?"
gcc $CFLAGS -DMSF_BUILD_ID='"ctrl2-nosticky"' -DMSF_ALG_TEST_NOSTICKY $SRC tests/runner.c tests/sha256.c \
  -o "$S/out/ctrl/runner_nosticky.exe" >> "$S/out/ctrl/build.log" 2>&1; echo "nosticky rc=$?"
cat "$S/out/ctrl/build.log"

R="$S/out/ctrl/runner.exe"
echo "===== sanity: normal runner accepts committed alg vectors ====="
"$R" verify tests/vectors/alg-f16.vec tests/vectors/alg-f32.vec tests/vectors/alg-f64.vec \
  > "$S/out/ctrl/sane.log" 2>&1; echo "rc=$?"
grep -E 'total|VERDICT' "$S/out/ctrl/sane.log"

"$PY" "$S/make_controls.py" "$PWD" "$S/out/ctrl" > "$S/out/ctrl/make.log" 2>&1; echo "make rc=$?"
cat "$S/out/ctrl/make.log"

FAIL=0
watch() { # $1 name, $2 runner, $3 vec...
  local name="$1" runner="$2"; shift 2
  "$runner" verify "$@" > "$S/out/ctrl/$name.log" 2>&1
  local rc=$?
  local nf=$(grep -c '^FAIL' "$S/out/ctrl/$name.log" || true)
  if [ "$rc" -ne 0 ] && grep -q 'VERDICT: FAIL' "$S/out/ctrl/$name.log"; then
    echo "control $name: REFUSED as required (rc=$rc, FAIL lines=$nf)"
  else
    echo "control $name: NOT REFUSED (rc=$rc)"; FAIL=1
  fi
}
watch qnan-inf-mutant "$R" "$S/out/ctrl/mut_qnan_inf.vec"
watch ulp-moved-hardest "$R" "$S/out/ctrl/mut_ulp.vec"
watch inexact-stripped-tie "$R" "$S/out/ctrl/mut_noinexact.vec"
watch mode-swap-subnormal "$R" "$S/out/ctrl/mut_modeswap.vec"
watch nosticky-kernel "$S/out/ctrl/runner_nosticky.exe" \
  tests/vectors/alg-f16.vec tests/vectors/alg-f32.vec tests/vectors/alg-f64.vec
echo "-- nosticky failures on ties lines (required > 0):"
grep '^FAIL' "$S/out/ctrl/nosticky-kernel.log" | grep -c 'mpfr-alg:ties' || true
grep '^FAIL' "$S/out/ctrl/nosticky-kernel.log" | grep 'mpfr-alg:ties' | head -3

echo "===== JAM build over committed vectors (EXPECTED PASS: equivalence) ====="
"$S/out/ctrl/runner_jam.exe" verify tests/vectors/alg-f16.vec tests/vectors/alg-f32.vec tests/vectors/alg-f64.vec \
  > "$S/out/ctrl/jam.log" 2>&1; echo "jam rc=$?"
grep -E 'total|VERDICT' "$S/out/ctrl/jam.log"

[ "$FAIL" = 0 ] && echo "NEGATIVE CONTROLS: all refused" || echo "NEGATIVE CONTROLS: FAIL"
echo "===== 05_controls done ====="
