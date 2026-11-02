#!/usr/bin/env bash
set -u
cd /c/Users/logan/source/repos/Muse-Softfloat
export TMPDIR=$PWD/scratch/parcel-w4trig/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-w4trig\tmp'
export TEMP="$TMP"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
O=scratch/parcel-w4trig/out
WT=worktrees/w4-trig
SRC="$WT/src/msf16.c $WT/src/msf32.c $WT/src/msf64.c $WT/src/msf_flags.c $WT/src/msf_wide.c $WT/src/msf_roundpack.c $WT/src/msf_string.c $WT/src/msf_math.c"
gcc -std=c11 -O2 -Wall scratch/parcel-w4trig/kernel_bench.c $SRC -I $WT/include -o $O/kernel_bench.exe > $O/kbench_build.log 2>&1
echo "kbench build rc=$?"; cat $O/kbench_build.log
$O/kernel_bench.exe
# decider-only rate at gate shape: 20000 varied f32 inputs through decide (prec 640 - upper bound cost)
PY=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
$PY scratch/parcel-w4trig/make_decide_inputs.py 20000 > $O/decide_in.txt
START=$(date +%s%N)
$WT/build/trig/trig_exhaustive.exe decide < $O/decide_in.txt > $O/decide_out.txt
END=$(date +%s%N)
echo "decide(640) 20000 lines rc=$? in $(( (END-START)/1000000 ))ms"
head -2 $O/decide_out.txt
