#!/usr/bin/env bash
set -u
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
W=$ROOT/worktrees/w3-str
S=$ROOT/scratch/parcel-str
export TMPDIR=$S/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-str\tmp'
export TEMP="$TMP"
cd "$W" || exit 9
PY=python
mkdir -p "$S/stdtail"
$PY tests/gen_vectors.py f16-exhaustive "$S/stdtail/f16-exhaustive.vec" > "$S/stdtail/gen-f16.log" 2>&1
echo "gen f16 rc=$?"
$PY tests/gen_vectors.py pack-sweep "$S/stdtail/pack-sweep.vec" 200000 > "$S/stdtail/gen-sweep.log" 2>&1
echo "gen sweep rc=$?"
grep -h . "$S/stdtail/gen-f16.log" "$S/stdtail/gen-sweep.log" | grep -E 'wrote|dropped'
build/str/msf_runner.exe verify "$S/stdtail/f16-exhaustive.vec" "$S/stdtail/pack-sweep.vec" > "$S/stdtail/verify.log" 2>&1
echo "verify rc=$?"
grep -E '^(file|total|VERDICT)' "$S/stdtail/verify.log"
