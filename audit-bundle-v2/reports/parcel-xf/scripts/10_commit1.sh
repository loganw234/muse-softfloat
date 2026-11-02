#!/usr/bin/env bash
set -uo pipefail
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
export TMPDIR="$ROOT/scratch/parcel-xf/tmp"
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-xf\tmp'
export TEMP="$TMP"
cd "$ROOT/worktrees/w2-xf" || exit 9
G="git -c safe.directory=$PWD"
$G add src/msf32.c src/msf64.c tests/gen_vectors_xf.py \
  tests/vectors/arith-xf.vec tests/vectors/fma-sqrt-xf.vec \
  tests/vectors/conv-xf.vec tests/vectors/compare-xf.vec \
  tests/vectors/traps-xf.vec tables/implemented.tsv \
  include/muse_softfloat.h src/msf_formats.h tests/msf_dispatch.h \
  docs/COVERAGE.tsv
$G status --porcelain
$G commit -F "$ROOT/scratch/parcel-xf/commit1.txt"
echo "commit exit=$?"
$G log --oneline -2
$G status --porcelain
