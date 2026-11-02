#!/usr/bin/env bash
# 00_env.sh - verifier-w5alg1 environment probe. Read-only.
set -u
COPY="$1"
echo "== verifier-w5alg1 env =="
echo "date: $(date '+%Y-%m-%d %H:%M:%S %z')"
echo "shell: $(bash --version | head -1)"
echo "gcc: $(gcc -dumpmachine) $(gcc -dumpversion)"
echo "MSF_PYTHON: ${MSF_PYTHON:-<unset>}"
"${MSF_PYTHON:-python3}" --version 2>&1
echo "mpfr header: $(ls /mingw64/include/mpfr.h 2>/dev/null || echo MISSING)"
echo "mpfr lib: $(ls /mingw64/lib/libmpfr.* 2>/dev/null | tr '\n' ' ' || echo MISSING)"
echo "arm cc: $(command -v arm-none-eabi-gcc || echo MISSING)"
echo "copy: $COPY"
git -C "$COPY" log --oneline -3
git -C "$COPY" status --short | head -5
echo "copy HEAD parent check:"
git -C "$COPY" merge-base --is-ancestor 7c3819c HEAD && echo "7c3819c is ancestor of HEAD"
