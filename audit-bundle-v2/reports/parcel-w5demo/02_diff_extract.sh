#!/usr/bin/env bash
set -u
WS=/c/Users/logan/source/repos/Muse-Softfloat
NEW=$WS/worktrees/w5-demo/demo/cache/ias15-extract
OLD=$WS/scratch/ias15/extract
for f in integrator_ias15_min.c gravity_basic_min.c reb_min.h sim_min.c ias15x.c; do
  echo "=== diff $f (scratch -> demo) ==="
  diff -u "$OLD/$f" "$NEW/$f" | head -60
  echo "(diff lines: $(diff "$OLD/$f" "$NEW/$f" | wc -l))"
done
echo "DIFF-CHECK DONE"
