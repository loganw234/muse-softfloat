#!/usr/bin/env bash
# fuzz 100k per direction family from vw_ref; run both runners.
R=/c/Users/logan/source/repos/Muse-Softfloat
export TMPDIR=$R/scratch/verifier-w3str/tmp
export TMP="C:\Users\logan\source\repos\Muse-Softfloat\scratch\verifier-w3str\tmp"
export TEMP="$TMP"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
cd "$R/scratch/verifier-w3str" || exit 9
PY="$R/.venv/Scripts/python.exe"
mkdir -p fuzz
for spec in "from-dec 100000 1101" "from-hex 100000 1102" "to-dec 100000 1103" "to-hex 100000 1104"; do
  set -- $spec
  "$PY" vw_gen.py fuzz "$1" "fuzz/vw-fuzz-$1.vec" "$2" "$3" > "fuzz/gen-$1.log" 2>&1
  echo "gen $1 exit=$? lines=$(wc -l < fuzz/vw-fuzz-$1.vec)"
done
ls -la fuzz/
