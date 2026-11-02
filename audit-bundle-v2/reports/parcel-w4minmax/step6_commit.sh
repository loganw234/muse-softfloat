#!/usr/bin/env bash
set -u
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w4-minmax || exit 9
G="git -c safe.directory=/c/Users/logan/source/repos/Muse-Softfloat/worktrees/w4-minmax"
$G add src/msf_performat.inc tests/gen_vectors_tier2.py \
  tests/vectors/minmax-f16.vec tests/vectors/minmax-f32.vec tests/vectors/minmax-f64.vec \
  tests/vectors/payload-f16.vec tests/vectors/payload-f32.vec tests/vectors/payload-f64.vec \
  tables/implemented.tsv include/muse_softfloat.h tests/msf_dispatch.h \
  docs/COVERAGE.tsv tests/VECTORS.md docs/metrics/briefs.jsonl || exit 1
echo "== staged =="
$G status --short
$G commit -F /c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w4minmax/commit-msg.txt || exit 1
echo "== tip =="
$G log --oneline -3
$G rev-parse HEAD
$G status --short
$G show --stat --oneline HEAD | head -25
