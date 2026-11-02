#!/usr/bin/env bash
# regen.sh - verifier-w5aug regen stops: gen_tables + gen_vectors_aug twice
# each, byte-compare runs against each other AND against the committed
# files (drift). Read-only w.r.t. the copy.
set -u
cd "$(dirname "$0")" || exit 9
COPY=../../worktrees/verify5-aug
export MSF_PYTHON="${MSF_PYTHON:-/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe}"
ulimit -v 3000000 2>/dev/null || true
R=regen
rm -rf "$R/gen1" "$R/gen2" "$R/vec1" "$R/vec2"
echo "--- gen_tables run 1"; "$MSF_PYTHON" "$COPY/tools/gen_tables.py" "$R/gen1" > logs/regen-gen1.log 2>&1 || { cat logs/regen-gen1.log; echo "REGEN: FAIL gen_tables/1"; exit 1; }
echo "--- gen_tables run 2"; "$MSF_PYTHON" "$COPY/tools/gen_tables.py" "$R/gen2" > logs/regen-gen2.log 2>&1 || { cat logs/regen-gen2.log; echo "REGEN: FAIL gen_tables/2"; exit 1; }
for f in include/muse_softfloat.h src/msf_formats.h tests/msf_dispatch.h docs/COVERAGE.tsv; do
  if cmp -s "$R/gen1/$f" "$R/gen2/$f"; then echo "stable: $f"; else echo "UNSTABLE: $f"; fi
  if cmp -s "$COPY/$f" "$R/gen1/$f"; then echo "matches-committed: $f"; else echo "DRIFT: $f differs from tables/"; fi
done
echo "--- gen_vectors_aug run 1"; "$MSF_PYTHON" "$COPY/tests/gen_vectors_aug.py" "$R/vec1" > logs/regen-vec1.log 2>&1 || { cat logs/regen-vec1.log; echo "REGEN: FAIL gen_vectors_aug/1"; exit 1; }
echo "--- gen_vectors_aug run 2"; "$MSF_PYTHON" "$COPY/tests/gen_vectors_aug.py" "$R/vec2" > logs/regen-vec2.log 2>&1 || { cat logs/regen-vec2.log; echo "REGEN: FAIL gen_vectors_aug/2"; exit 1; }
for f in aug-f16.vec aug-f32.vec aug-f64.vec; do
  if cmp -s "$R/vec1/$f" "$R/vec2/$f"; then echo "stable: $f"; else echo "UNSTABLE: $f"; fi
  if cmp -s "$COPY/tests/vectors/$f" "$R/vec1/$f"; then echo "matches-committed: $f"; else echo "DRIFT: tests/vectors/$f differs from generator output"; fi
done
echo REGEN.SH: DONE
