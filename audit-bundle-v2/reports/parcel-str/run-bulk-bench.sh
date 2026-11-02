#!/usr/bin/env bash
set -u
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
W=$ROOT/worktrees/w3-str
S=$ROOT/scratch/parcel-str
export TMPDIR=$S/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-str\tmp'
export TEMP="$TMP"
mkdir -p "$TMPDIR" "$S/bulk"
cd "$W" || exit 9
PY=$ROOT/.venv/Scripts/python.exe
for kind in from-decimal to-decimal from-hex to-hex; do
  echo "== $kind =="
  time $PY tests/gen_vectors_str.py bulk "$kind" "$S/bulk/bench-$kind.vec" 3000 4242
done
ls -la "$S/bulk/"
