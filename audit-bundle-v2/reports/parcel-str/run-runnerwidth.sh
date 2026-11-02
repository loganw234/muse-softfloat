#!/usr/bin/env bash
set -u
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
export TMPDIR=$ROOT/scratch/parcel-str/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-str\tmp'
export TEMP="$TMP"
mkdir -p "$TMPDIR"
bash "$ROOT/softfloat-bootstrap-kit/tools/ledger.sh" append "$ROOT/ledger" parcel-str "Directed run: from_* 4886 and f64 to_* pass; runner to_* width bug (retkind SPECIAL) fails all f16/f32 to_*" < "$ROOT/scratch/parcel-str/runnerwidth-body.txt"
echo "append rc=$?"
bash "$ROOT/softfloat-bootstrap-kit/tools/ledger.sh" urgent "$ROOT/ledger" parcel-str runner-width "parcel-str: runner to_* calls f64 for f16/f32 (retkind SPECIAL, want argkinds[0])" < "$ROOT/scratch/parcel-str/runnerwidth-urgent.txt"
echo "urgent rc=$?"
