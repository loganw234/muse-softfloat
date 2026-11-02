#!/usr/bin/env bash
R=/c/Users/logan/source/repos/Muse-Softfloat
G=$R/scratch/verifier-w3str/regen
V=$R/worktrees/verify3-str/tests/vectors
echo "=== from-decimal diff:"
diff "$V/from-decimal-str.vec" "$G/from-decimal-str.vec"
echo "=== from-hex diff:"
diff "$V/from-hex-str.vec" "$G/from-hex-str.vec"
