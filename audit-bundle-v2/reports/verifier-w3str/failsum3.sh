#!/usr/bin/env bash
R=/c/Users/logan/source/repos/Muse-Softfloat
L=$R/scratch/verifier-w3str/replay-str.log
V=$R/worktrees/verify3-str/tests/vectors
echo "=== from-hex sample FAILs:"
grep '^FAIL tests/vectors/from-hex-str.vec:\(15\|16\|20\|22\|28\|46\|48\|58\|59\|108\|244\|348\|546\|658\|682\|891\|984\|1004\|1045\|1047\|1064\|1096\|1120\|1224\|1244\|1264\|1284\) ' "$L" | head -40
