#!/usr/bin/env bash
R=/c/Users/logan/source/repos/Muse-Softfloat
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
cd "$R/scratch/verifier-w3str" || exit 9
echo "=== adv non-snan non-tie fails: all from_hex?"
grep '^FAIL' adv-fails.txt | grep -vi 'snan' | grep -v 'from_hex' | grep -vc 'to_decimal\|to-dec\|from_decimal'
echo "above = lines outside (from_hex OR dec-tie) classes (expect 0)"
echo "=== from_hex adv fails: $(grep '^FAIL' adv-fails.txt | grep -c 'from_hex')"
echo "=== regen from-hex diff line numbers:"
grep -n '^[0-9<>]' /dev/null 2>/dev/null
diff "$R/worktrees/verify3-str/tests/vectors/from-hex-str.vec" regen/from-hex-str.vec | grep '^[0-9]' | head -20
echo "=== committed from-dec line 118 + siblings:"
sed -n '118,123p' "$R/worktrees/verify3-str/tests/vectors/from-decimal-str.vec" | cut -c1-100
