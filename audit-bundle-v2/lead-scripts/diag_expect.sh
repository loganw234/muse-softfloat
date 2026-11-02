#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat/muse-softfloat || exit 9
echo "--- expect.txt str tags ---"
grep 'exact-str' build/smoke/expect.txt
echo "--- verify.log prov str ---"
grep '^prov exact-str' build/smoke/verify.log
echo "--- expect-count check lines in verify.log ---"
grep -n 'expect' build/smoke/verify.log | head -8
