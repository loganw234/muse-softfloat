#!/usr/bin/env bash
# probe2a: build the copy's own runner, replay committed f32 vectors per family
set -u
W=/c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify-f32
S=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w1f32
export PATH=/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH
cd "$W" || exit 9
gcc -std=c11 -O2 -Wall -Wextra -ffp-contract=off \
  -DMSF_BUILD_ID='"verifier-w1f32"' \
  -Iinclude -Isrc \
  src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c \
  tests/runner.c tests/sha256.c -o "$S/msf_runner.exe" > "$S/runner-build.log" 2>&1
echo "BUILD_EXIT=$?"
V=tests/vectors
for f in arith-f32 fma-sqrt-f32 conv-int-f32 rint-misc-f32 toint-f32 compare-f32 encodings-f32; do
  "$S/msf_runner.exe" verify "$V/$f.vec" > "$S/verify-$f.log" 2>&1
  echo "$f EXIT=$? :: $(grep -E 'VERDICT|FAIL' "$S/verify-$f.log" | head -n 5)"
done
echo done-probe2a
