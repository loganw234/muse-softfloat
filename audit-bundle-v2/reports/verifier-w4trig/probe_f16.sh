#!/bin/bash
# Probe I: f16 exhaustive rerun on the copy (vehicle build, counters on).
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
V=$ROOT/scratch/verifier-w4trig
cd "$ROOT" || exit 9
mkdir -p $V/out
$V/tmp/trigx.exe f16 > $V/out/f16_gate.log 2>&1
echo "f16 rc=$?"
tail -8 $V/out/f16_gate.log
echo "=== mismatch signature tally (first-field groups) ==="
grep '^MISMATCH' $V/out/f16_gate.log | sed 's/in=.*got=/got=/' | sort | uniq -c | sort -rn | head -20
echo "=== total mismatch lines ==="
grep -c '^MISMATCH' $V/out/f16_gate.log
