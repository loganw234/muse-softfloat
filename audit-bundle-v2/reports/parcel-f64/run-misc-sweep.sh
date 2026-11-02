#!/usr/bin/env bash
set -uo pipefail
cd /c/Users/logan/source/repos/Muse-Softfloat
export TMPDIR=$PWD/scratch/parcel-f64/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-f64\tmp'
export TEMP="$TMP"
echo "start $(date -Iseconds)"
time .venv/Scripts/python.exe scratch/parcel-f64/gen_misc_sweep.py > scratch/parcel-f64/misc-sweep-gen.log 2>&1
echo "gen rc=$?"; cat scratch/parcel-f64/misc-sweep-gen.log
cd worktrees/w1-f64
time build/smoke/msf_runner.exe verify build/w1/misc-sweep.vec > build/w1/logs/misc-sweep-verify.log 2>&1
rc=$?; echo "verify rc=$rc end $(date -Iseconds)"
grep -E '^(file|prov|total|VERDICT)' build/w1/logs/misc-sweep-verify.log
grep '^FAIL' build/w1/logs/misc-sweep-verify.log | head -20 || true
exit $rc
