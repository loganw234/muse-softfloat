#!/usr/bin/env bash
R=/c/Users/logan/source/repos/Muse-Softfloat
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
cd "$R/worktrees/verify3-str/tests/vectors" || exit 9
echo "=== committed zero SPEC=0 to-hex rows:"
grep -h 'A=0000[^0-9A-F]\|A=00000000[^0-9A-F]\|A=0000000000000000[^0-9A-F]' to-hex-str.vec | grep 'SPEC=0' | head -6
echo "=== committed zero exact-enough rows:"
grep -h 'SPEC=-1' to-hex-str.vec | grep -i 'A=0\{4,\} ' | head -4
