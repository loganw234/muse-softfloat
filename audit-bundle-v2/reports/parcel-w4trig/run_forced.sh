#!/usr/bin/env bash
set -u
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w4-trig
export TMPDIR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w4trig/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-w4trig\tmp'
export TEMP="$TMP"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
O=/c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w4trig/out
for exe in trig_stage1 trig_stage2; do
  START=$(date +%s)
  build/trig/$exe.exe f16 > "$O/forced_${exe}_f16.log" 2>&1
  echo "$exe f16 rc=$? in $(( $(date +%s) - START ))s"
  cat "$O/forced_${exe}_f16.log"
done
bash /c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w4trig/run_wc.sh build/trig/trig_stage1.exe wc_stage1
bash /c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w4trig/run_wc.sh build/trig/trig_stage2.exe wc_stage2
bash /c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w4trig/run_f64seed.sh build/trig/trig_stage2.exe 777 65536 f64seed_stage2
