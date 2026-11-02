#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w6sanitize || exit 9
echo "--- clean-build.log ---"
cat dup/build/sanitize-trap/canaries/clean-build.log
echo "--- full default log head ---"
head -30 sanitize-default.log
