#!/usr/bin/env bash
set -uo pipefail
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w1-f64
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export TMPDIR=$PWD/build/w1/tmp
export TMP="$(cygpath -w "$TMPDIR")"
export TEMP="$TMP"
SRC="src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c"
for opt in O0 Os; do
  echo "=== -$opt $(date -Iseconds)"
  gcc -std=c11 -$opt -Wall -Wextra -Werror -ffp-contract=off -DMSF_BUILD_ID="\"opt-$opt\"" $SRC tests/runner.c tests/sha256.c -o "build/w1/runner-$opt.exe" > "build/w1/logs/opt-$opt-build.log" 2>&1
  echo "build rc=$?"
  cat "build/w1/logs/opt-$opt-build.log"
  "build/w1/runner-$opt.exe" verify build/w1/quick-add.vec build/w1/cross-sweep-seed2.vec > "build/w1/logs/opt-$opt-verify.log" 2>&1
  echo "verify rc=$?"
  grep -E '^(total|VERDICT)' "build/w1/logs/opt-$opt-verify.log"
  grep '^FAIL' "build/w1/logs/opt-$opt-verify.log" | head -3 || true
done
