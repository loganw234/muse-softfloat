#!/usr/bin/env bash
# Probe 3b: baseline-twin verify (cost ratio), exact totals, negative
# control (trap build must still refuse a corrupted vector).
set -u
cd "$(dirname "$0")/.." || exit 9
ROOT=$PWD
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export MSF_PYTHON="/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe"
PY="$MSF_PYTHON"
{
cd tree || exit 8
echo "===== baseline twin: unit + full VECS verify ====="
$PY ../scripts/verify_driver.py "$(cygpath -w "$PWD")" "$(cygpath -w "$PWD/build-san/msf_runner_base.exe")" baseline "$(cygpath -w "$ROOT/logs/10_base_verify.log")"
echo "driver rc=$?"
echo
echo "===== exact totals (all-files, trap twin, verbatim summary lines) ====="
$PY ../scripts/count_run.py "$(cygpath -w "$PWD")" "$(cygpath -w "$PWD/build-san/msf_runner_trap.exe")"
echo
echo "===== negative control: corrupted expected bit vs trap twin ====="
awk 'BEGIN{d=0} /^msf16_is_signaling/ && !d {for(i=1;i<=NF;i++) if($i=="->") $(i+1)=($(i+1)=="1"?"0":"1"); d=1} {print}' \
    tests/vectors/encodings-f16.vec > build-san/corrupt.vec
./build-san/msf_runner_trap.exe verify build-san/corrupt.vec > build-san/corrupt.log 2>&1
rc=$?
echo "corrupt-vs-trap rc=$rc (must be nonzero)"
grep -E 'VERDICT|FAIL' build-san/corrupt.log | head -3
./build-san/msf_runner_base.exe verify build-san/corrupt.vec > build-san/corrupt-base.log 2>&1
echo "corrupt-vs-base rc=$? (must be nonzero)"
} > "$ROOT/logs/09_baseline_and_controls.log" 2>&1
tail -40 "$ROOT/logs/09_baseline_and_controls.log"
