#!/usr/bin/env bash
# Probe 3c: trap-UBSan over the `standard` extras: generated f16-exhaustive
# + 200k pack-sweep vectors, and the aug_exhaustive pool harness.
set -u
cd "$(dirname "$0")/.." || exit 9
ROOT=$PWD
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export MSF_PYTHON="/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe"
PY="$MSF_PYTHON"
{
cd tree || exit 8
export TMPDIR=$PWD/build-san/tmp
export TMP="$(cygpath -w "$TMPDIR" 2>/dev/null || echo "$TMPDIR")"
export TEMP="$TMP"
echo "===== generate standard extras ====="
T0=$(date +%s)
$PY tests/gen_vectors.py f16-exhaustive "build-san/f16-exhaustive.vec" > build-san/gen-f16.log 2>&1
echo "gen f16 rc=$? dt=$(($(date +%s)-T0))s"; grep -E 'wrote|dropped' build-san/gen-f16.log
T0=$(date +%s)
$PY tests/gen_vectors.py pack-sweep "build-san/pack-sweep.vec" 200000 > build-san/gen-sweep.log 2>&1
echo "gen sweep rc=$? dt=$(($(date +%s)-T0))s"; grep -E 'wrote|dropped' build-san/gen-sweep.log
ls -la build-san/*.vec
echo
echo "===== trap twin verify extras ====="
T0=$(date +%s)
./build-san/msf_runner_trap.exe verify "build-san/f16-exhaustive.vec" "build-san/pack-sweep.vec" > build-san/verify-extras-trap.log 2>&1
echo "trap extras rc=$? dt=$(($(date +%s)-T0))s"
grep -E '^(total|VERDICT)' build-san/verify-extras-trap.log
T0=$(date +%s)
./build-san/msf_runner_base.exe verify "build-san/f16-exhaustive.vec" "build-san/pack-sweep.vec" > build-san/verify-extras-base.log 2>&1
echo "base extras rc=$? dt=$(($(date +%s)-T0))s"
grep -E '^(total|VERDICT)' build-san/verify-extras-base.log
echo
echo "===== aug_exhaustive pool harness (trap build) ====="
SRC="src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c src/msf_string.c src/msf_math.c src/msf_alg.c src/msf_aug.c"
gcc -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off -fsanitize=undefined -fsanitize-undefined-trap-on-error -fno-sanitize-recover=all $SRC tests/aug_exhaustive.c -o build-san/aug_exhaustive_trap.exe > build-san/build-aug-trap.log 2>&1
echo "aug trap build rc=$?"; head -3 build-san/build-aug-trap.log
T0=$(date +%s)
./build-san/aug_exhaustive_trap.exe pool > build-san/aug-pool-trap.log 2>&1
echo "aug trap pool rc=$? dt=$(($(date +%s)-T0))s"
grep -E '^(aug_exhaustive|  kind|VERDICT)' build-san/aug-pool-trap.log
gcc -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off $SRC tests/aug_exhaustive.c -o build-san/aug_exhaustive_base.exe > build-san/build-aug-base.log 2>&1
echo "aug base build rc=$?"
T0=$(date +%s)
./build-san/aug_exhaustive_base.exe pool > build-san/aug-pool-base.log 2>&1
echo "aug base pool rc=$? dt=$(($(date +%s)-T0))s"
grep -E '^(aug_exhaustive|  kind|VERDICT)' build-san/aug-pool-base.log
} > "$ROOT/logs/11_trap_standard_extras.log" 2>&1
cat "$ROOT/logs/11_trap_standard_extras.log"
