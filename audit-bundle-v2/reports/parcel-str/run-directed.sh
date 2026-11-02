#!/usr/bin/env bash
set -u
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
W=$ROOT/worktrees/w3-str
export TMPDIR=$ROOT/scratch/parcel-str/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-str\tmp'
export TEMP="$TMP"
mkdir -p "$TMPDIR"
cd "$W" || exit 9
PY=$ROOT/.venv/Scripts/python.exe
$PY tools/gen_tables.py > "$ROOT/scratch/parcel-str/gen-tables.log" 2>&1
echo "gen_tables rc=$?"
cat "$ROOT/scratch/parcel-str/gen-tables.log"
git -c safe.directory="$W" status --porcelain
$PY tests/gen_vectors_str.py directed tests/vectors > "$ROOT/scratch/parcel-str/gen-directed.log" 2>&1
echo "gen directed rc=$?"
cat "$ROOT/scratch/parcel-str/gen-directed.log"
ls -la tests/vectors/*str*.vec
wc -l tests/vectors/*str*.vec
