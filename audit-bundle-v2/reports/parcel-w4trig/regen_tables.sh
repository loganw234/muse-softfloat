#!/usr/bin/env bash
set -u
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w4-trig
export TMPDIR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w4trig/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-w4trig\tmp'
export TEMP="$TMP"
PY=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
O=/c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w4trig/out
$PY tools/gen_tables.py > $O/gen_tables.log 2>&1
echo "gen_tables rc=$?"; cat $O/gen_tables.log
$PY tools/gen_trig_tables.py $O/msf_trig_tables.check.h > $O/gen_trig_check.log 2>&1
echo "gen_trig_tables rc=$?"; cat $O/gen_trig_check.log
cmp src/msf_trig_tables.h $O/msf_trig_tables.check.h && echo "trig tables regen byte-identical"
grep -c "sin_pi" docs/COVERAGE.tsv
grep "sin_pi" docs/COVERAGE.tsv | head -2
grep "msf_call_msf32_sin_pi" tests/msf_dispatch.h | head -2
git -c safe.directory=$PWD status --short | head -30
