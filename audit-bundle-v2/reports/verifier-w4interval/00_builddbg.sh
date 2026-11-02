#!/usr/bin/env bash
# 00_builddbg.sh - debug the host-runner build failure.
set -u
VROOT="/c/Users/logan/source/repos/Muse-Softfloat"
COPY="$VROOT/worktrees/verify4-interval"
OUT="$VROOT/scratch/verifier-w4interval"
CC="/c/msys64/mingw64/bin/gcc.exe"
echo "hello build test"
echo "cc exists: $(ls -la "$CC")"
echo "src present: $(ls "$COPY/src/msf64.c" "$COPY/board/interval_host.c" "$COPY/tests/sha256.c")"
echo "--- tiny compile ---"
echo 'int main(void){return 0;}' > "$OUT/build/tiny.c"
"$CC" -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off "$OUT/build/tiny.c" -o "$OUT/build/tiny.exe"
echo "tiny rc=$?"
