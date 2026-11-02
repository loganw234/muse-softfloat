#!/usr/bin/env bash
set -uo pipefail
cd /c/Users/logan/source/repos/Muse-Softfloat
echo "== regate step2 start $(date -Iseconds) =="
echo "-- check_tininess probe (reference restatement) --"
.venv/Scripts/python.exe scratch/parcel-f64/check_tininess.py 2>&1
echo "-- rebuild runner via smoke-quick --"
t0=$(date +%s)
bash scratch/parcel-f64/smoke-quick.sh > scratch/parcel-f64/regate-build.log 2>&1
rc=$?; t1=$(date +%s); echo "smoke-quick rc=$rc seconds=$((t1-t0))"; cat scratch/parcel-f64/regate-build.log
[ $rc -eq 0 ] || exit $rc
echo "-- regenerate directed into directed-check and compare to committed --"
t0=$(date +%s)
bash scratch/parcel-f64/gen-directed.sh > scratch/parcel-f64/regate-gen-directed.log 2>&1
rc=$?; t1=$(date +%s); echo "gen-directed rc=$rc seconds=$((t1-t0))"; cat scratch/parcel-f64/regate-gen-directed.log
[ $rc -eq 0 ] || exit $rc
cd worktrees/w1-f64
for f in arith-f64 conv-f64 misc-f64 compare-f64 nan-f64; do
  if cmp -s "build/w1/directed-check/$f.vec" "tests/vectors/$f.vec"; then
    echo "DIRECTED IDENTICAL $f.vec"
  else
    echo "DIRECTED DIFFERS $f.vec"
    diff "tests/vectors/$f.vec" "build/w1/directed-check/$f.vec" | head -40
  fi
done
echo "-- verify directed-check --"
t0=$(date +%s)
bash ../../scratch/parcel-f64/verify-directed.sh > ../../scratch/parcel-f64/regate-verify-directed.log 2>&1
rc=$?; t1=$(date +%s); echo "verify-directed rc=$rc seconds=$((t1-t0))"; cat ../../scratch/parcel-f64/regate-verify-directed.log
echo "-- verify committed directed explicitly --"
build/smoke/msf_runner.exe verify tests/vectors/arith-f64.vec tests/vectors/conv-f64.vec tests/vectors/misc-f64.vec tests/vectors/compare-f64.vec tests/vectors/nan-f64.vec > build/w1/logs/regate-committed-directed.log 2>&1
rc2=$?; echo "committed-directed rc=$rc2"
grep -E '^(file|prov|total|VERDICT)' build/w1/logs/regate-committed-directed.log || true
grep '^FAIL' build/w1/logs/regate-committed-directed.log | head -20 || true
# arith line 1824 evidence: show the line itself
echo "-- arith-f64.vec line 1824 --"
sed -n '1824p' tests/vectors/arith-f64.vec
cd /c/Users/logan/source/repos/Muse-Softfloat
echo "-- sweep seed 0xF64 210000 --"
t0=$(date +%s)
bash scratch/parcel-f64/run-sweep.sh 210000 > scratch/parcel-f64/regate-sweep1.log 2>&1
rc3=$?; t1=$(date +%s); echo "sweep1 rc=$rc3 seconds=$((t1-t0))"; cat scratch/parcel-f64/regate-sweep1.log
echo "-- sweep seed 0xC0FFEE 150000 --"
t0=$(date +%s)
bash scratch/parcel-f64/run-sweep2.sh > scratch/parcel-f64/regate-sweep2.log 2>&1
rc4=$?; t1=$(date +%s); echo "sweep2 rc=$rc4 seconds=$((t1-t0))"; cat scratch/parcel-f64/regate-sweep2.log
echo "-- misc sweep 120000 --"
t0=$(date +%s)
bash scratch/parcel-f64/run-misc-sweep.sh > scratch/parcel-f64/regate-misc.log 2>&1
rc5=$?; t1=$(date +%s); echo "misc rc=$rc5 seconds=$((t1-t0))"; cat scratch/parcel-f64/regate-misc.log
echo "== regate step2 end $(date -Iseconds) verify=$rc committed=$rc2 sweep1=$rc3 sweep2=$rc4 misc=$rc5 =="
[ $rc -eq 0 ] && [ $rc2 -eq 0 ] && [ $rc3 -eq 0 ] && [ $rc4 -eq 0 ] && [ $rc5 -eq 0 ]
