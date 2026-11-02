#!/usr/bin/env bash
set -u
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
cd /c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w6sanitize/scripts || exit 9
mkdir -p ../logs/rev
gcc -dumpmachine; gcc -dumpversion
gcc -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off strnlen_probe.c -o strnlen_probe.exe > ../logs/rev/strnlen-probe.log 2>&1
echo "strnlen -std=c11 rc=$?"
cat ../logs/rev/strnlen-probe.log
./strnlen_probe.exe || true
