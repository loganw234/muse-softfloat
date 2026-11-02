#!/usr/bin/env bash
# dbg.sh - diagnose the empty-log build failure.
set -u
SCR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w5log2
COPY=/c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify5-log2
GCC=/c/msys64/mingw64/bin/gcc.exe
echo "gcc=$GCC"
ls -la "$GCC"
echo "compile probe:"
"$GCC" --version
echo "rc=$?"
cd "$SCR" || exit 9
ulimit -v 4194304
echo "ulimit set"
"$GCC" -std=c11 -O2 -fsyntax-only -I"$COPY/include" vlog2.c
echo "syntax rc=$?"
