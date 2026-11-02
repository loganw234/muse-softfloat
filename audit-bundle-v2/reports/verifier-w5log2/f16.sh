#!/usr/bin/env bash
# f16.sh - full binary16 exhaustive differential (log pair, 5 modes).
set -u
export PATH=/c/msys64/mingw64/bin:$PATH
SCR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w5log2
ulimit -v 4194304
cd "$SCR" || exit 9
./build/vlog2.exe f16 > logs/f16.log 2>&1
echo "rc=$?"
tail -3 logs/f16.log
