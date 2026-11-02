#!/usr/bin/env bash
# verifier-w164: regenerate with the PARCEL BRANCH generator (w1-f64),
# diff against branch vectors (expect: clean) and against copy vectors.
set -uo pipefail
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w1-f64
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
SCR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w1f64
rm -rf "$SCR/branch-regen"
mkdir -p "$SCR/branch-regen" build/w1v/tmp
export TMPDIR=$PWD/build/w1v/tmp
export TMP="$(cygpath -w "$TMPDIR")"
export TEMP="$TMP"
PY=../../.venv/Scripts/python.exe
LOG=$SCR/v-branchregen.log
{
echo "=== branch generator directed regen ==="
$PY tests/gen_vectors_f64.py directed "$SCR/branch-regen"
echo "rc=$?"
for f in "$SCR/branch-regen"/*; do
  b=$(basename "$f")
  if cmp -s "$f" "tests/vectors/$b"; then
    echo "BRANCH-IDENTICAL $b"
  else
    echo "BRANCH-DRIFT $b"
    diff "$f" "tests/vectors/$b" | head -n 8
  fi
done
} > "$LOG" 2>&1
echo "done rc=$?"
cat "$LOG"
