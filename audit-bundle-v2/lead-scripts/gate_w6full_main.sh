#!/usr/bin/env bash
set -u
cd "$(dirname "$0")/../../muse-softfloat" || exit 9
export PATH="/c/Program Files/Git/cmd:/c/Program Files/Git/mingw64/bin:/c/Program Files/Git/usr/bin:/usr/bin:$PATH"
export TMPDIR="$PWD/../scratch/lead/tmp" TMP="$PWD/../scratch/lead/tmp" TEMP="$PWD/../scratch/lead/tmp"
mkdir -p "$TMPDIR"
export MSF_PYTHON="$PWD/../.venv/Scripts/python.exe"
bash tools/run.sh standard > ../scratch/lead/gate_w6full_standard.log 2>&1
r1=$?
echo "standard rc=$r1"
grep -E "budget standard|total .* passed" ../scratch/lead/gate_w6full_standard.log | tail -n 4
bash tools/run.sh sanitize > ../scratch/lead/gate_w6full_sanitize.log 2>&1
r2=$?
echo "sanitize rc=$r2"
grep -E "budget sanitize|canary|total .* passed" ../scratch/lead/gate_w6full_sanitize.log | tail -n 10
bash examples/host/build.sh > ../scratch/lead/gate_w6full_example.log 2>&1
r3=$?
echo "example rc=$r3"
tail -n 2 ../scratch/lead/gate_w6full_example.log
[ $r1 -eq 0 ] && [ $r2 -eq 0 ] && [ $r3 -eq 0 ]
