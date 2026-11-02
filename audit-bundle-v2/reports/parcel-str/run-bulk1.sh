#!/usr/bin/env bash
set -u
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
W=$ROOT/worktrees/w3-str
S=$ROOT/scratch/parcel-str
export TMPDIR=$S/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-str\tmp'
export TEMP="$TMP"
cd "$W" || exit 9
R=build/smoke/msf_runner.exe
date '+bulk from start %H:%M:%S'
"$R" verify "$S/bulk/from-decimal-600k.vec" > "$S/bulk-from-dec.log" 2>&1
echo "from-dec rc=$?"
grep -E '^(file|total|VERDICT)' "$S/bulk-from-dec.log"
grep '^FAIL' "$S/bulk-from-dec.log" | head -20
"$R" verify "$S/bulk/from-hex-300k.vec" > "$S/bulk-from-hex.log" 2>&1
echo "from-hex rc=$?"
grep -E '^(file|total|VERDICT)' "$S/bulk-from-hex.log"
grep '^FAIL' "$S/bulk-from-hex.log" | head -20
date '+bulk from done %H:%M:%S'
grep '^msf64_' "$S/bulk/to-decimal-700k.vec" > "$S/bulk/to-decimal-f64only.vec"
grep '^msf64_' "$S/bulk/to-hex-300k.vec" > "$S/bulk/to-hex-f64only.vec"
wc -l "$S/bulk/to-decimal-f64only.vec" "$S/bulk/to-hex-f64only.vec"
"$R" verify "$S/bulk/to-decimal-f64only.vec" > "$S/bulk-to-dec-f64.log" 2>&1
echo "to-dec f64 rc=$?"
grep -E '^(file|total|VERDICT)' "$S/bulk-to-dec-f64.log"
grep '^FAIL' "$S/bulk-to-dec-f64.log" | head -20
"$R" verify "$S/bulk/to-hex-f64only.vec" > "$S/bulk-to-hex-f64.log" 2>&1
echo "to-hex f64 rc=$?"
grep -E '^(file|total|VERDICT)' "$S/bulk-to-hex-f64.log"
grep '^FAIL' "$S/bulk-to-hex-f64.log" | head -20
date '+bulk f64-to done %H:%M:%S'
