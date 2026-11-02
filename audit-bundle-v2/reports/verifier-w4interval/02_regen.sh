#!/usr/bin/env bash
# 02_regen.sh - regenerate catalogue from the copy's generator, byte-compare.
set -u
VROOT="/c/Users/logan/source/repos/Muse-Softfloat"
COPY="$VROOT/worktrees/verify4-interval"
OUT="$VROOT/scratch/verifier-w4interval"
export MSF_PYTHON="/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
mkdir -p "$OUT/build"
"$MSF_PYTHON" "$COPY/tests/gen_interval_catalogue.py" "$OUT/build/regen.tsv"
echo "gen rc=$?"
if cmp -s "$COPY/tests/interval_catalogue.tsv" "$OUT/build/regen.tsv"; then
  echo "REGEN: byte-identical"
else
  echo "REGEN: DIFFERS"
  cmp "$COPY/tests/interval_catalogue.tsv" "$OUT/build/regen.tsv" | head -5
  echo "--- diff line count ---"
  diff "$COPY/tests/interval_catalogue.tsv" "$OUT/build/regen.tsv" | grep -c '^[<>]'
  echo "--- first differing data row ---"
  diff "$COPY/tests/interval_catalogue.tsv" "$OUT/build/regen.tsv" | head -20
fi
