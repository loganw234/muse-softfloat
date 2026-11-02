#!/usr/bin/env bash
set -euo pipefail
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w1-f64
export TMPDIR=$PWD/build/w1/tmp
export TMP="$(cygpath -w "$TMPDIR")"
export TEMP="$TMP"
G="git -c safe.directory=C:/Users/logan/source/repos/Muse-Softfloat/worktrees/w1-f64"
$G status --short
$G add src/msf64.c tables/implemented.tsv include/muse_softfloat.h tests/msf_dispatch.h docs/COVERAGE.tsv tests/gen_vectors_f64.py tests/vectors/arith-f64.vec tests/vectors/conv-f64.vec tests/vectors/misc-f64.vec tests/vectors/compare-f64.vec tests/vectors/nan-f64.vec
$G status --short
$G commit -F ../../scratch/parcel-f64/commit1-msg.txt
$G log --oneline -3
$G status --short
