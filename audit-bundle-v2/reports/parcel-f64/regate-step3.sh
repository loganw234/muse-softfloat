#!/usr/bin/env bash
set -uo pipefail
cd /c/Users/logan/source/repos/Muse-Softfloat
echo "== regate step3 start $(date -Iseconds) =="
echo "MSF_TESTFLOAT_GEN is set inside berkeley.sh per-case; berkeley.sh line:"
grep MSF_TESTFLOAT_GEN scratch/parcel-f64/berkeley.sh
FAILS=0
run_one() {
  local label="$1"; shift
  local t0 t1 rc
  t0=$(date +%s)
  bash scratch/parcel-f64/berkeley.sh one "$@" > "scratch/parcel-f64/regate-berk-${label}.log" 2>&1
  rc=$?; t1=$(date +%s)
  echo "case $label rc=$rc seconds=$((t1-t0))"
  cat "scratch/parcel-f64/regate-berk-${label}.log"
  [ $rc -ne 0 ] && FAILS=$((FAILS+1))
  return 0
}
for rm in te tp tn ta; do
  run_one "f64_mul-${rm}-l1" f64_mul "$rm" 1 0
  run_one "f64_div-${rm}-l1" f64_div "$rm" 1 0
done
run_one "f64_mul-te-l2t2000000" f64_mul te 2 2000000
for rm in te tp tn ta; do
  run_one "f64_mulAdd-${rm}-l1t2000000" f64_mulAdd "$rm" 1 2000000
done
run_one "f64_eq-l1" f64_eq - 1 0
echo "== regate step3 end $(date -Iseconds) fails=$FAILS =="
exit $FAILS
