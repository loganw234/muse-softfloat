#!/usr/bin/env bash
R=/c/Users/logan/source/repos/Muse-Softfloat
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
cd "$R/worktrees/verify3-str/tests/vectors" || exit 9
echo "=== 1.2346 rows:"
grep -h '1\.2346' to-decimal-str.vec | head -6
echo "=== OUT=0x2 rows:"
grep -h 'OUT=.*0x2p' to-hex-str.vec | head -6
echo "=== 1.00 carry rows (frac all zero with prec>0 on nonzero):"
grep -h 'OUT=0x1\.0\+p' to-hex-str.vec | head -8
echo "=== subnormal nonzero exact-enough:"
grep -h 'OUT=0x0\.[0-9a-f]*[1-9a-f][0-9a-f]*p-14\b' to-hex-str.vec | head -4
grep -h 'OUT=0x0\.[0-9a-f]*[1-9a-f][0-9a-f]*p-126\b' to-hex-str.vec | head -4
grep -h 'OUT=.*p-1022' to-hex-str.vec | head -6
