#!/usr/bin/env bash
R=/c/Users/logan/source/repos/Muse-Softfloat
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
cd "$R/worktrees/verify3-str" || exit 9
echo "=== implemented.tsv CR count (od):"
tr -cd '\r' < tables/implemented.tsv | wc -c
wc -l tables/implemented.tsv
echo "=== parent version CR count:"
git -c safe.directory="$R/worktrees/verify3-str" show 548a1b9:tables/implemented.tsv | tr -cd '\r' | wc -c
echo "=== main-repo version CR count:"
tr -cd '\r' < "$R/muse-softfloat/tables/implemented.tsv" | wc -c
echo "=== str vec files CR count:"
for f in tests/vectors/*str*.vec; do printf '%s ' "$f"; tr -cd '\r' < "$f" | wc -c; done
echo "=== src/msf_string.c CR count:"
tr -cd '\r' < src/msf_string.c | wc -c
