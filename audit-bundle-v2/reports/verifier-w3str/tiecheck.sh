#!/usr/bin/env bash
R=/c/Users/logan/source/repos/Muse-Softfloat
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
cd "$R/scratch/verifier-w3str" || exit 9
echo "=== offtie fails on regular runner (expect 0):"
grep '^FAIL' adv.log | grep -c 'vw:offtie'
echo "=== ties fails:"
grep '^FAIL' adv.log | grep -c 'vw:ties'
echo "=== beyondh fails:"
grep '^FAIL' adv.log | grep -c 'vw:beyondh'
grep '^FAIL' adv.log | grep 'vw:beyondh' | cut -c1-120 | head -8
echo "=== ties fails detail:"
grep '^FAIL' adv.log | grep 'vw:ties' | cut -c1-140 | head -8
