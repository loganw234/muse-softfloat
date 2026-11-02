#!/usr/bin/env bash
set -u
W=/c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify-f32
S=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w1f32
cd "$W" || exit 9
export TMPDIR=$W/build/smoke/tmp TMP=$(cygpath -w "$W/build/smoke/tmp" 2>/dev/null) TEMP=$(cygpath -w "$W/build/smoke/tmp" 2>/dev/null)
/c/msys64/mingw64/bin/gcc -std=c11 -O2 -Wall -Wextra -ffp-contract=off \
  -Iinclude -Isrc \
  src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c \
  "$S/probe_div.c" -o "$S/probe_div.exe" > "$S/probe_div-build.log" 2>&1
echo "BUILD_EXIT=$?"
"$S/probe_div.exe"
