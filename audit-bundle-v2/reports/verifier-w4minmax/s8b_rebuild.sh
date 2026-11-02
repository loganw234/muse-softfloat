#!/usr/bin/env bash
# verifier-w4minmax s8b: rebuild fixed runner with visible errors.
set -u
COPY=/c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify4-minmax
SCR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w4minmax
OUT=$SCR/out-fixed
cp "$COPY/tests/msf_dispatch.h" "$OUT/"
ls "$OUT/"
export PATH=/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH
gcc -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off -DMSF_BUILD_ID='"fixed-experiment"' -I "$OUT/fxinc" -I "$OUT/fxsrc" -I "$OUT" "$OUT/fxsrc"/msf16.c "$OUT/fxsrc"/msf32.c "$OUT/fxsrc"/msf64.c "$OUT/fxsrc"/msf_flags.c "$OUT/fxsrc"/msf_wide.c "$OUT/fxsrc"/msf_roundpack.c "$OUT/fxsrc"/msf_string.c "$OUT/runner.c" "$OUT/sha256.c" -o "$OUT/fx_runner.exe"
echo "fx_build_rc=$?"
