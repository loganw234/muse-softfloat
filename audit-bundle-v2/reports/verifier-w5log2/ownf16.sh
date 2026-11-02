#!/usr/bin/env bash
# ownf16.sh - the COPY's own f16 exhaustive leg, outside the copy.
set -u
export PATH=/c/msys64/mingw64/bin:$PATH
SCR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w5log2
ulimit -v 4194304
cd "$SCR" || exit 9
./build/own_exhaustive.exe f16 > logs/ownf16.log 2>&1
echo "rc=$?"
tail -3 logs/ownf16.log
grep -c MISMATCH logs/ownf16.log
