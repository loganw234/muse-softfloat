#!/usr/bin/env bash
set -uo pipefail
cd /c/Users/logan/source/repos/Muse-Softfloat
echo "== regate step4 controls start $(date -Iseconds) =="
t0=$(date +%s)
bash scratch/parcel-f64/run-controls.sh > scratch/parcel-f64/regate-controls.log 2>&1
rc=$?; t1=$(date +%s); echo "controls rc=$rc seconds=$((t1-t0))"; cat scratch/parcel-f64/regate-controls.log
echo "== regate step5 smoke start $(date -Iseconds) =="
cd worktrees/w1-f64
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
mkdir -p build/smoke/tmp build/w1/logs
export TMPDIR=$PWD/build/smoke/tmp
export TMP="$(cygpath -w "$TMPDIR")"
export TEMP="$TMP"
t0=$(date +%s)
bash tools/run.sh smoke > build/w1/logs/regate-run-smoke.log 2>&1
rc2=$?; t1=$(date +%s); echo "smoke rc=$rc2 seconds=$((t1-t0))"; cat build/w1/logs/regate-run-smoke.log
echo "== regate step5 standard start $(date -Iseconds) =="
t0=$(date +%s)
bash tools/run.sh standard > build/w1/logs/regate-run-standard.log 2>&1
rc3=$?; t1=$(date +%s); echo "standard rc=$rc3 seconds=$((t1-t0))"; cat build/w1/logs/regate-run-standard.log
echo "== regate step45 end $(date -Iseconds) controls=$rc smoke=$rc2 standard=$rc3 =="
[ $rc -eq 0 ] && [ $rc2 -eq 0 ] && [ $rc3 -eq 0 ]
