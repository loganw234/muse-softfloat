#!/usr/bin/env bash
# 00-env.sh - inventory before results (verifier-w5attr).
set -u
echo "== env =="
echo "bash: $(which bash) $BASH_VERSION"
echo "MSF_PYTHON=$MSF_PYTHON"
"$MSF_PYTHON" --version 2>&1
echo "gcc64: $(/c/msys64/mingw64/bin/gcc -dumpmachine) $(/c/msys64/mingw64/bin/gcc -dumpversion)"
echo "git: $(git --version)"
echo "copy HEAD: $(git -C "$COPY" log --format='%H %s' -1)"
echo "parent: 889ec2ef2dcaf579e6e3fd52d8e31ec61450d921"
