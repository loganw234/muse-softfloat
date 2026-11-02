#!/usr/bin/env bash
# Post-merge final gate sequence for parcel-f64. Run after merging
# the lead kernel/ingest/control fix commit into w1-f64.
set -uo pipefail
cd /c/Users/logan/source/repos/Muse-Softfloat
echo "postmerge start $(date -Iseconds)"
bash scratch/parcel-f64/run-smoke.sh > scratch/parcel-f64/postmerge-smoke.log 2>&1
echo "smoke outer rc=$?"
tail -30 scratch/parcel-f64/postmerge-smoke.log
bash scratch/parcel-f64/berkeley.sh cmp > scratch/parcel-f64/postmerge-cmp.log 2>&1
echo "cmp rc=$?"
bash scratch/parcel-f64/berkeley.sh A > scratch/parcel-f64/postmerge-A.log 2>&1
echo "A rc=$?"
bash scratch/parcel-f64/berkeley.sh B > scratch/parcel-f64/postmerge-B.log 2>&1
echo "B rc=$?"
bash scratch/parcel-f64/berkeley.sh C > scratch/parcel-f64/postmerge-C.log 2>&1
echo "C rc=$?"
bash scratch/parcel-f64/berkeley.sh one f64_rem - 2 1000000 > scratch/parcel-f64/postmerge-rem.log 2>&1
echo "rem-extra rc=$?"
bash scratch/parcel-f64/verify-directed.sh > scratch/parcel-f64/postmerge-directed.log 2>&1
echo "directed(build-check) rc=$?"
bash scratch/parcel-f64/run-sweep.sh 210000 > scratch/parcel-f64/postmerge-sweep.log 2>&1
echo "sweep rc=$?"
bash scratch/parcel-f64/run-misc-sweep.sh > scratch/parcel-f64/postmerge-misc.log 2>&1
echo "misc rc=$?"
bash scratch/parcel-f64/run-controls.sh > scratch/parcel-f64/postmerge-controls.log 2>&1
echo "controls rc=$?"
cd worktrees/w1-f64
build/smoke/msf_runner.exe verify tests/vectors/arith-f64.vec tests/vectors/conv-f64.vec tests/vectors/misc-f64.vec tests/vectors/compare-f64.vec tests/vectors/nan-f64.vec > build/w1/logs/postmerge-committed-directed.log 2>&1
echo "committed-directed rc=$?"
grep -E '^(file|prov|total|VERDICT)' build/w1/logs/postmerge-committed-directed.log
echo "postmerge end $(date -Iseconds)"
