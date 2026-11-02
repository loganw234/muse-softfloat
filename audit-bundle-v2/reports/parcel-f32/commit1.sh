#!/usr/bin/env bash
set -eu
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w1-f32
export TMPDIR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-f32/tmp
export TMP="$(cygpath -w "$TMPDIR")"
export TEMP="$TMP"
G="git -c safe.directory=C:/Users/logan/source/repos/Muse-Softfloat/worktrees/w1-f32"
$G add src/msf32.c tables/implemented.tsv include/muse_softfloat.h docs/COVERAGE.tsv tests/msf_dispatch.h tests/gen_vectors_f32.py tests/vectors/arith-f32.vec tests/vectors/compare-f32.vec tests/vectors/conv-int-f32.vec tests/vectors/fma-sqrt-f32.vec tests/vectors/rint-misc-f32.vec tests/vectors/toint-f32.vec
$G status --short
$G commit -F /c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-f32/commit1-msg.txt
$G log --oneline -2
$G status --short
