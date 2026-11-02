#!/usr/bin/env bash
R=/c/Users/logan/source/repos/Muse-Softfloat
L=$R/scratch/verifier-w3str/replay-str.log
echo "=== to-decimal FAILs:"
grep '^FAIL tests/vectors/to-decimal-str.vec' "$L"
echo
echo "=== from-decimal FAIL line 3276 + context:"
grep '^FAIL tests/vectors/from-decimal-str.vec:3276' "$L"
sed -n '3276p' "$R/worktrees/verify3-str/tests/vectors/from-decimal-str.vec"
echo
echo "=== count snan-related FAILs in from-decimal:"
grep '^FAIL tests/vectors/from-decimal-str.vec' "$L" | grep -c 'IN=.*[sS][nN][aA][nN]'
echo "=== non-snan FAILs in from-decimal:"
grep '^FAIL tests/vectors/from-decimal-str.vec' "$L" | grep -v 'IN=.*[sS][nN][aA][nN]'
