#!/usr/bin/env bash
# verifier-w164 debug: minimal NaN-ordering probes through the copy runner.
set -uo pipefail
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify-f64
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
mkdir -p build/w1v/tmp
export TMPDIR=$PWD/build/w1v/tmp
export TMP="$(cygpath -w "$TMPDIR")"
export TEMP="$TMP"
SCR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w1f64
printf '%s\n' \
 'msf64_scale_b te 7ff8000000000000 7ff0000000000001 -> 7ff4000000000001 01 dbg:nan-order' \
 'msf64_add te 7ff8000000000000 7ff0000000000001 -> 7ff4000000000001 01 dbg:nan-order' \
 'msf64_scale_b te 7ff0000000000001 7ff8000000000000 -> 7ff4000000000001 01 dbg:nan-order' \
 > "$SCR/dbg-nan.vec"
build/smoke/msf_runner.exe verify "$SCR/dbg-nan.vec"
