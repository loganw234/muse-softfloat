#!/usr/bin/env bash
set -u
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
W=$ROOT/worktrees/w3-str
S=$ROOT/scratch/parcel-str
export TMPDIR=$S/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-str\tmp'
export TEMP="$TMP"
cd "$W" || exit 9
bash tools/run.sh standard > "$S/standard1.log" 2>&1
echo "standard rc=$?"
grep -E '^(==|drift|unit:|total|VERDICT|type|symbol|target undefined|control|negative|RUN.SH|budget|file tests)' "$S/standard1.log" | head -60
