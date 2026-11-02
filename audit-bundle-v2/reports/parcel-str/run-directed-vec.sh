#!/usr/bin/env bash
set -u
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
W=$ROOT/worktrees/w3-str
export TMPDIR=$ROOT/scratch/parcel-str/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-str\tmp'
export TEMP="$TMP"
cd "$W" || exit 9
R=build/smoke/msf_runner.exe
"$R" verify tests/vectors/from-decimal-str.vec tests/vectors/from-hex-str.vec tests/vectors/to-decimal-str.vec tests/vectors/to-hex-str.vec > "$ROOT/scratch/parcel-str/directed1.log" 2>&1
echo "runner rc=$?"
grep -E '^(file|prov|total|VERDICT)' "$ROOT/scratch/parcel-str/directed1.log"
echo "--- first 40 FAIL lines ---"
grep '^FAIL' "$ROOT/scratch/parcel-str/directed1.log" | head -40
echo "--- fail count ---"
grep -c '^FAIL' "$ROOT/scratch/parcel-str/directed1.log" || true
