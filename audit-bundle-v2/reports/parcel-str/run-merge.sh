#!/usr/bin/env bash
set -u
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
W=$ROOT/worktrees/w3-str
export TMPDIR=$ROOT/scratch/parcel-str/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-str\tmp'
export TEMP="$TMP"
mkdir -p "$TMPDIR"
cp "$W/src/msf_string.c" "$ROOT/scratch/parcel-str/msf_string.c.mine"
rm "$W/src/msf_string.c"
cd "$W" || exit 9
git -c safe.directory="$W" merge --no-edit bc15b2c
echo "merge rc=$?"
git -c safe.directory="$W" log --oneline -3
echo "--- lead stub head ---"
head -40 src/msf_string.c
echo "--- lead commit files ---"
git -c safe.directory="$W" show --stat --oneline bc15b2c | head -30
cp "$ROOT/scratch/parcel-str/msf_string.c.mine" "$W/src/msf_string.c"
git -c safe.directory="$W" status --porcelain
