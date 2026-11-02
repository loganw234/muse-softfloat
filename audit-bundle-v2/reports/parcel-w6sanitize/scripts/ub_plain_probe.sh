#!/usr/bin/env bash
set -u
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w6-sanitize || exit 9
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
D=/c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w6sanitize/logs/neg2
mkdir -p "$D/tmp"
export TMPDIR="$D/tmp"
export TMP="$(cygpath -w "$TMPDIR")"
export TEMP="$TMP"
gcc -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off tests/sanitize_canary_ub.c -o "$D/ub-plain.exe" > "$D/ub-plain-build2.log" 2>&1
echo "build rc=$?"
cat "$D/ub-plain-build2.log"
"$D/ub-plain.exe" > "$D/ub-plain2.log" 2>&1
echo "run rc=$?"
cat "$D/ub-plain2.log"
