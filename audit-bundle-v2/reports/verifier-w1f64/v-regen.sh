#!/usr/bin/env bash
# verifier-w164 (1c): regen directed sets to temp with the copy's own
# generator; diff against committed vectors. Also regen gen_tables.
set -uo pipefail
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify-f64
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
SCR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w1f64
rm -rf "$SCR/regen-tmp" "$SCR/gentab-tmp"
mkdir -p "$SCR/regen-tmp" build/regen/tmp
export TMPDIR=$PWD/build/regen/tmp
export TMP="$(cygpath -w "$TMPDIR")"
export TEMP="$TMP"
PY=../../.venv/Scripts/python.exe
LOG=$SCR/v-regen.log
{
echo "=== directed regen ==="
$PY tests/gen_vectors_f64.py directed "$SCR/regen-tmp"
echo "directed rc=$?"
ls "$SCR/regen-tmp"
for f in "$SCR/regen-tmp"/*; do
  b=$(basename "$f")
  echo "--- diff $b ---"
  diff "$f" "tests/vectors/$b" > "$SCR/regen-diff-$b.txt" 2>&1
  echo "diff rc=$? lines: $(wc -l < "$SCR/regen-diff-$b.txt")"
done
echo "=== gen_tables regen ==="
$PY tools/gen_tables.py "$SCR/gentab-tmp" > "$SCR/gentab.log" 2>&1
echo "gen_tables rc=$?"
for f in include/muse_softfloat.h src/msf_formats.h tests/msf_dispatch.h docs/COVERAGE.tsv; do
  if cmp -s "$f" "$SCR/gentab-tmp/$f"; then echo "IDENTICAL $f"; else echo "DRIFT $f"; fi
done
} > "$LOG" 2>&1
echo "regen done rc=$?"
tail -n 20 "$LOG"
