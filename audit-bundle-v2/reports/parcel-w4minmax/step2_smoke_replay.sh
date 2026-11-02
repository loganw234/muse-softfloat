#!/usr/bin/env bash
set -u
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w4-minmax || exit 9
export MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
S=/c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w4minmax
bash tools/run.sh smoke > "$S/smoke1.log" 2>&1
rc=$?
echo "smoke rc=$rc"
tail -5 "$S/smoke1.log"
[ $rc -eq 0 ] || exit 1
T2="tests/vectors/minmax-f16.vec tests/vectors/minmax-f32.vec tests/vectors/minmax-f64.vec tests/vectors/payload-f16.vec tests/vectors/payload-f32.vec tests/vectors/payload-f64.vec"
awk '!/^#/ && NF>0 {print $NF}' $T2 | sort | uniq -c | awk '{print $2, $1}' > build/smoke/expect-t2.txt
cat build/smoke/expect-t2.txt
build/smoke/msf_runner.exe verify --expect-counts build/smoke/expect-t2.txt $T2 > "$S/replay-directed.log" 2>&1
rc=$?
echo "directed replay rc=$rc"
cat "$S/replay-directed.log"
exit $rc
