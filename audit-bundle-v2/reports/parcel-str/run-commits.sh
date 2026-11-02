#!/usr/bin/env bash
set -u
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
W=$ROOT/worktrees/w3-str
S=$ROOT/scratch/parcel-str
export TMPDIR=$S/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-str\tmp'
export TEMP="$TMP"
cd "$W" || exit 9
G="git -c safe.directory=$W"
$G add src/msf_string.c tables/implemented.tsv include/muse_softfloat.h src/msf_formats.h tests/msf_dispatch.h docs/COVERAGE.tsv
$G commit -F "$S/commit1.txt"
echo "commit1 rc=$?"
$G add tests/gen_vectors_str.py tests/vectors/from-decimal-str.vec tests/vectors/from-hex-str.vec tests/vectors/to-decimal-str.vec tests/vectors/to-hex-str.vec
$G commit -F "$S/commit2.txt"
echo "commit2 rc=$?"
$G log --oneline -5
$G status --porcelain
