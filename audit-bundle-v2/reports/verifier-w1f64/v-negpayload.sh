#!/usr/bin/env bash
# verifier-w164: negative-NaN payload-order observation probe (note only).
set -uo pipefail
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify-f64
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
mkdir -p build/w1v/tmp
export TMPDIR=$PWD/build/w1v/tmp
export TMP="$(cygpath -w "$TMPDIR")"
export TEMP="$TMP"
SCR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w1f64
printf '%s\n' \
 'msf64_total_order - fff8000000000000 fff8000000000001 -> 1 -- obs:negpayload' \
 'msf64_total_order - fff8000000000001 fff8000000000000 -> 0 -- obs:negpayload' \
 'msf64_total_order - fff8000000000001 fffc000000000000 -> 1 -- obs:negpayload' \
 'msf64_total_order - fffc000000000000 fff8000000000001 -> 0 -- obs:negpayload' \
 'msf64_total_order - fff0000000000001 fff4000000000000 -> 1 -- obs:negpayload' \
 'msf64_total_order - fff4000000000000 fff0000000000001 -> 0 -- obs:negpayload' \
 'msf64_total_order_mag - fff8000000000000 fff8000000000001 -> 1 -- obs:negpayload' \
 'msf64_total_order_mag - fff8000000000001 fff8000000000000 -> 0 -- obs:negpayload' \
 > "$SCR/dbg-negpayload.vec"
build/smoke/msf_runner.exe verify "$SCR/dbg-negpayload.vec"
