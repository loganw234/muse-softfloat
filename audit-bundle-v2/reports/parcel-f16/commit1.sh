#!/usr/bin/env bash
set -euo pipefail
export TMPDIR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-f16/tmp
export TMP="$(cygpath -w "$TMPDIR")"
export TEMP="$TMP"
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w2-f16
GIT="git -c safe.directory=C:/Users/logan/source/repos/Muse-Softfloat/worktrees/w2-f16"
$GIT add src/msf16.c tests/gen_vectors_f16.py \
  tests/vectors/arith-f16.vec tests/vectors/fma-sqrt-f16.vec \
  tests/vectors/conv-int-f16.vec tests/vectors/toint-f16.vec \
  tests/vectors/rint-misc-f16.vec tests/vectors/compare-f16.vec \
  tables/implemented.tsv docs/COVERAGE.tsv include/muse_softfloat.h \
  src/msf_formats.h tests/msf_dispatch.h
$GIT status --short
$GIT commit -F /c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-f16/commit1-msg.txt
$GIT log --oneline -2
$GIT status --short
$GIT show --stat HEAD | head -30
