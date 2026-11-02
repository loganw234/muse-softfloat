#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w5demo/clonetest || exit 9
git ls-files | grep -iE 'kiss|rebound|extract|cache'
echo "---end---"
