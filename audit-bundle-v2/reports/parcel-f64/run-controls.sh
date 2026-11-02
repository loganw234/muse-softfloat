#!/usr/bin/env bash
set -uo pipefail
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w1-f64
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
mkdir -p build/w1/tmp build/w1/controls build/w1/logs
export TMPDIR=$PWD/build/w1/tmp
export TMP="$(cygpath -w "$TMPDIR")"
export TEMP="$TMP"
export MSF_TESTFLOAT_GEN='C:\Users\logan\source\repos\Muse-Softfloat\scratch\oracles\TestFloat-3e\build\Linux-x86_64-GCC\testfloat_gen.exe'
PY=../../.venv/Scripts/python.exe
SRC="src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c"
echo "controls start $(date -Iseconds)"
# ensure a passing berkeley file exists (f64_add te l1 first 20000)
$PY tests/berkeley_ingest.py --fn f64_add --rm te --level 1 --take 20000 --out build/w1/quick-add.vec > build/w1/logs/control-quick-ingest.log 2>&1
echo "ingest rc=$?"
$PY ../../scratch/parcel-f64/make_controls.py > build/w1/logs/controls-make.log 2>&1
echo "make rc=$?"; cat build/w1/logs/controls-make.log
R=build/smoke/msf_runner.exe
check_refused() {
    local name="$1" file="$2" runner="${3:-$R}"
    "$runner" verify "$file" > "build/w1/logs/control-${name}.log" 2>&1
    local rc=$?
    echo "control $name rc=$rc (want nonzero)"
    grep -E '^(file|total|VERDICT)' "build/w1/logs/control-${name}.log" || true
    grep '^FAIL' "build/w1/logs/control-${name}.log" | head -3 || true
    if [ $rc -eq 0 ]; then echo "control $name NOT REFUSED"; return 1; fi
    return 0
}
check_pass() {
    local name="$1" file="$2" runner="${3:-$R}"
    "$runner" verify "$file" > "build/w1/logs/control-${name}.log" 2>&1
    local rc=$?
    echo "control $name rc=$rc (want 0)"
    grep -E '^(file|total|VERDICT)' "build/w1/logs/control-${name}.log" || true
    return $rc
}
FAILS=0
check_pass berkeley-base build/w1/quick-add.vec || FAILS=$((FAILS+1))
check_refused flip-result build/w1/controls/berkeley-flip-result.vec || FAILS=$((FAILS+1))
check_refused flip-flag build/w1/controls/berkeley-flip-flag.vec || FAILS=$((FAILS+1))
# wrong tininess build against smallest-normal boundary in berkeley mul and directed arith
gcc -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off -DMSF_TININESS_AFTER_ROUNDING=0 -DMSF_BUILD_ID='"tininess-before-control"' $SRC tests/runner.c tests/sha256.c -o build/w1/controls/msf_runner_tbefore.exe > build/w1/logs/control-tbefore-build.log 2>&1
echo "tininess-before build rc=$?"
$PY tests/berkeley_ingest.py --fn f64_mul --rm te --level 1 --out build/w1/controls/berkeley-mul-te-l1.vec > build/w1/logs/control-mul-ingest.log 2>&1
echo "mul ingest rc=$?"; cat build/w1/logs/control-mul-ingest.log
check_refused tininess-before-mul build/w1/controls/berkeley-mul-te-l1.vec build/w1/controls/msf_runner_tbefore.exe || FAILS=$((FAILS+1))
check_refused tininess-before-arith build/w1/directed-check/arith-f64.vec build/w1/controls/msf_runner_tbefore.exe || FAILS=$((FAILS+1))
# nan payload masking: pass only under nan-class
check_pass nan-payload-nanclass build/w1/controls/nan-payload-nanclass.vec || FAILS=$((FAILS+1))
check_refused nan-payload-exact build/w1/controls/nan-payload-exact.vec || FAILS=$((FAILS+1))
echo "controls done fails=$FAILS $(date -Iseconds)"
exit $FAILS
