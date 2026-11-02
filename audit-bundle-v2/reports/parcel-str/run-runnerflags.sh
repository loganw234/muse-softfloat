#!/usr/bin/env bash
set -u
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
export TMPDIR=$ROOT/scratch/parcel-str/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-str\tmp'
export TEMP="$TMP"
mkdir -p "$TMPDIR"
bash "$ROOT/softfloat-bootstrap-kit/tools/ledger.sh" append "$ROOT/ledger" parcel-str "RULINGS received (all 6 accepted); merged bc15b2c; runner char-from flags token bug at runner.c:236" < "$ROOT/scratch/parcel-str/runnerflags-body.txt"
echo "append rc=$?"
bash "$ROOT/softfloat-bootstrap-kit/tools/ledger.sh" urgent "$ROOT/ledger" parcel-str runner-flags "parcel-str: runner.c:236 reads C= token as flags for char-from lines" < "$ROOT/scratch/parcel-str/runnerflags-urgent.txt"
echo "urgent rc=$?"
