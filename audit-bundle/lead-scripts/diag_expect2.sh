#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat/muse-softfloat || exit 9
ls build/smoke/ build/standard/ 2>/dev/null
echo "--- any expect lines ---"
grep -rn 'expect-count' build/smoke/ build/standard/ 2>/dev/null | head -10
echo "--- str in smoke expect ---"
grep -c 'exact-str' build/smoke/expect.txt build/standard/expect.txt 2>/dev/null
echo "--- tails ---"
tail -4 build/smoke/verify.log
