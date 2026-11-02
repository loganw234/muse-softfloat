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
date '+bulk gen start %H:%M:%S'
$PY tests/gen_vectors_str.py bulk from-decimal "$S/bulk/from-decimal-600k.vec" 600000 20261027
$PY tests/gen_vectors_str.py bulk to-decimal "$S/bulk/to-decimal-700k.vec" 700002 20261028
$PY tests/gen_vectors_str.py bulk from-hex "$S/bulk/from-hex-300k.vec" 300000 20261029
$PY tests/gen_vectors_str.py bulk to-hex "$S/bulk/to-hex-300k.vec" 300000 20261030
$PY tests/gen_vectors_str.py f16-exhaustive "$S/bulk/f16-exhaustive.vec"
date '+bulk gen done %H:%M:%S'
ls -la "$S/bulk/"
sha256sum "$S/bulk/"*.vec > "$S/bulk/SHA256SUMS.txt"
cat "$S/bulk/SHA256SUMS.txt"
