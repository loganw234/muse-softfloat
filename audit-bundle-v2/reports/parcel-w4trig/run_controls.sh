#!/usr/bin/env bash
set -u
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w4-trig
export TMPDIR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w4trig/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-w4trig\tmp'
export TEMP="$TMP"
PY=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
O=/c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w4trig/out
R=build/smoke/msf_runner.exe
$PY /c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w4trig/make_controls.py
echo "make rc=$?"
for name in pos_subset nc_quadrant_sign nc_delta_sign nc_directed_side nc_noninteger_reduction; do
  "$R" verify "$O/controls/$name.vec" > "$O/controls/$name.log" 2>&1
  rc=$?
  echo "$name rc=$rc : $(grep -E '^total|^VERDICT' "$O/controls/$name.log" | tr '\n' ' ')"
done
# dropped-limb mutant summaries (from run_wc.sh droplimb run)
grep -h '^wc .* f64:' $O/wc_droplimb_*.log
