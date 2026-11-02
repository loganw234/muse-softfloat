#!/usr/bin/env bash
# verifier-w4minmax s3: byte-identical regeneration of table outputs
# (4 files) and directed Tier 2 vectors (6 files).
set -u
COPY=/c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify4-minmax
SCR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w4minmax
export MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
OUT=$SCR/out-regen
mkdir -p "$OUT/tmp-tables" "$OUT/tmp-vec"
cd "$COPY" || exit 9
echo "== table regeneration =="
"$MSF_PYTHON" tools/gen_tables.py "$OUT/tmp-tables" > "$OUT/gen-tables.log" 2>&1
echo "gen_tables_rc=$?"
for f in include/muse_softfloat.h src/msf_formats.h tests/msf_dispatch.h docs/COVERAGE.tsv; do
  if cmp -s "$f" "$OUT/tmp-tables/$f"; then echo "IDENTICAL $f"; else echo "DIFF $f"; fi
done
echo "== directed vector regeneration =="
"$MSF_PYTHON" tests/gen_vectors_tier2.py directed "$OUT/tmp-vec" > "$OUT/gen-directed.log" 2>&1
echo "gen_directed_rc=$?"
cat "$OUT/gen-directed.log"
for f in minmax-f16 minmax-f32 minmax-f64 payload-f16 payload-f32 payload-f64; do
  if cmp -s "tests/vectors/$f.vec" "$OUT/tmp-vec/$f.vec"; then
    echo "IDENTICAL $f.vec"
  else
    echo "DIFF $f.vec: $(diff "tests/vectors/$f.vec" "$OUT/tmp-vec/$f.vec" | wc -l) diff-lines"
    diff "tests/vectors/$f.vec" "$OUT/tmp-vec/$f.vec" | head -12
  fi
done
exit 0
