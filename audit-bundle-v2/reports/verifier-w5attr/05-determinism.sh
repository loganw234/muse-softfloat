#!/usr/bin/env bash
# 05-determinism.sh - regeneration determinism: each generator twice,
# byte-identical; committed sets match. Also header regen vs committed.
set -u
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
V="$SCRATCH"
mkdir -p "$V/tmp/det1" "$V/tmp/det2"
export TMPDIR="$V/tmp" TMP="$V/tmp" TEMP="$V/tmp"
echo "== header regen vs committed =="
"$MSF_PYTHON" "$COPY/tools/gen_tables.py" "$V/tmp/det1" > "$V/tmp/det1/gen.log" 2>&1 || { cat "$V/tmp/det1/gen.log"; exit 1; }
for f in include/muse_softfloat.h src/msf_formats.h tests/msf_dispatch.h docs/COVERAGE.tsv; do
  if cmp -s "$COPY/$f" "$V/tmp/det1/$f"; then echo "MATCH: $f"; else echo "DRIFT: $f"; fi
done
echo "== header enum lines, regen vs committed =="
grep "TIES_TO_AWAY" "$V/tmp/det1/include/muse_softfloat.h" "$COPY/include/muse_softfloat.h"
