#!/usr/bin/env bash
# dbg2.sh - capture gcc diagnostics to a file.
set -u
SCR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w5log2
COPY=/c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify5-log2
GCC=/c/msys64/mingw64/bin/gcc.exe
cd "$SCR" || exit 9
"$GCC" -std=c11 -O2 -fsyntax-only -I"$COPY/include" vlog2.c > logs/dbg2.log 2>&1
echo "rc=$?"
echo "--- log bytes: $(wc -c < logs/dbg2.log)"
cat logs/dbg2.log
