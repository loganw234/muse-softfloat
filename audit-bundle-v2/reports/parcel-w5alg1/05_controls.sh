#!/usr/bin/env bash
# 05_controls.sh - the brief's negative controls, each watched
# REFUSED by the real runner (Git Bash).
set -u
ulimit -v 2097152 || echo "ulimit -v unsupported here (recorded)"
WS=/c/Users/logan/source/repos/Muse-Softfloat
cd "$WS/worktrees/w5-alg1" || exit 9
S="$WS/scratch/parcel-w5alg1"
mkdir -p "$S/out/ctrl" "$S/tmp"
export TMPDIR="$S/tmp"
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-w5alg1\tmp'
export TEMP="$TMP"
export MSF_PYTHON="$WS/.venv/Scripts/python.exe"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
PY="$MSF_PYTHON"
SRC="src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c src/msf_string.c src/msf_math.c src/msf_alg.c"
CFLAGS="-std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off"

echo "===== build runners (normal + truncated-stage mutant) ====="
gcc $CFLAGS -DMSF_BUILD_ID='"ctrl"' $SRC tests/runner.c tests/sha256.c \
  -o "$S/out/ctrl/runner.exe" > "$S/out/ctrl/build.log" 2>&1; echo "normal rc=$?"
gcc $CFLAGS -DMSF_BUILD_ID='"ctrl-trunc"' -DMSF_ALG_TEST_TRUNC $SRC tests/runner.c tests/sha256.c \
  -o "$S/out/ctrl/runner_trunc.exe" >> "$S/out/ctrl/build.log" 2>&1; echo "trunc rc=$?"
cat "$S/out/ctrl/build.log"

echo "===== sanity: normal runner accepts committed alg vectors ====="
"$S/out/ctrl/runner.exe" verify tests/vectors/alg-f16.vec tests/vectors/alg-f32.vec tests/vectors/alg-f64.vec \
  > "$S/out/ctrl/sane.log" 2>&1; echo "rc=$?"
grep -E 'total|VERDICT' "$S/out/ctrl/sane.log"

"$PY" "$S/make_controls.py" "$PWD" "$S/out/ctrl" > "$S/out/ctrl/make.log" 2>&1; echo "make rc=$?"
cat "$S/out/ctrl/make.log"

FAIL=0
watch() { # $1 name, $2 runner, $3 vec
  "$2" verify "$3" > "$S/out/ctrl/$1.log" 2>&1
  rc=$?
  nf=$(grep -c '^FAIL' "$S/out/ctrl/$1.log" || true)
  if [ "$rc" -ne 0 ] && grep -q 'VERDICT: FAIL' "$S/out/ctrl/$1.log"; then
    echo "control $1: REFUSED as required (rc=$rc, FAIL lines=$nf)"
  else
    echo "control $1: NOT REFUSED (rc=$rc)"; FAIL=1
  fi
}
R="$S/out/ctrl/runner.exe"
watch ulp-moved-hardest "$R" "$S/out/ctrl/mut_ulp.vec"
watch specials-negzero-flip "$R" "$S/out/ctrl/mut_negzero.vec"
watch specials-qnan-payload "$R" "$S/out/ctrl/mut_qnan.vec"
watch specials-negfinite "$R" "$S/out/ctrl/mut_negfinite.vec"
watch inexact-stripped "$R" "$S/out/ctrl/mut_noinexact.vec"
watch directed-mode-swap "$R" "$S/out/ctrl/mut_dirswap.vec"
watch truncated-stage-width "$S/out/ctrl/runner_trunc.exe" tests/vectors/alg-f64.vec
[ "$FAIL" = 0 ] && echo "NEGATIVE CONTROLS: all refused" || echo "NEGATIVE CONTROLS: FAIL"
echo "===== 05_controls done ====="
