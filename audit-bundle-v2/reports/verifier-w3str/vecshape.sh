#!/usr/bin/env bash
R=/c/Users/logan/source/repos/Muse-Softfloat
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
cd "$R/worktrees/verify3-str/tests/vectors" || exit 9
echo "=== BUF= lines in committed str vecs:"
grep -c 'BUF=' from-decimal-str.vec from-hex-str.vec to-decimal-str.vec to-hex-str.vec
echo "=== huge-precision rows:"
grep -h '1000000\|SPEC=100\|SPEC=40' to-decimal-str.vec to-hex-str.vec | head -8
echo "=== min_digits-floor row (1.23456 prec 2 min 5):"
grep -h '1.2346e+00' to-decimal-str.vec | head -4
echo "=== subnormal to-hex exact-enough rows:"
grep -h '0x0\.' to-hex-str.vec | head -6
echo "=== carry rows (0x2p or 1.00 carry):"
grep -h 'OUT=0x2p\|OUT=-0x2p\|OUT=0x1\.00.*p-14\b' to-hex-str.vec | head -6
echo "=== wrapped (backslash) lines:"
grep -c '\\$' from-decimal-str.vec to-decimal-str.vec
echo "=== OUT=~ lines:"
grep -c 'OUT=~' to-decimal-str.vec to-hex-str.vec
