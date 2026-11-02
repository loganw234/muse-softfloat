#!/usr/bin/env bash
# 01_rebuild_run.sh - rebuild host runner from the copy, rerun catalogue.
# Strict flags, contraction off. No -D overrides: shipped defaults apply.
set -u
VROOT="/c/Users/logan/source/repos/Muse-Softfloat"
COPY="$VROOT/worktrees/verify4-interval"
OUT="$VROOT/scratch/verifier-w4interval"
export MSF_PYTHON="/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
CC="gcc.exe"
mkdir -p "$OUT/build"
# shellcheck disable=SC2086
$CC -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off \
  -I"$COPY/include" \
  "$COPY"/src/msf16.c "$COPY"/src/msf32.c "$COPY"/src/msf64.c \
  "$COPY"/src/msf_flags.c "$COPY"/src/msf_wide.c "$COPY"/src/msf_roundpack.c \
  "$COPY"/src/msf_string.c \
  "$COPY"/board/interval_workload.c "$COPY"/board/interval_host.c \
  "$COPY"/tests/sha256.c \
  -o "$OUT/build/interval_host.exe" 2>"$OUT/build/build.log" || {
  echo "BUILD FAILED"; cat "$OUT/build/build.log"; exit 1; }
echo "build clean: -Wall -Wextra -Werror, contraction off"
"$OUT/build/interval_host.exe" "$COPY/tests/interval_catalogue.tsv" \
  > "$OUT/build/host_out.txt" 2>"$OUT/build/host_err.txt" || {
  echo "RUN FAILED"; cat "$OUT/build/host_err.txt"; exit 1; }
tail -n 3 "$OUT/build/host_out.txt"
grep -h "HOST_SHA256" "$OUT/build/host_out.txt"
wc -l "$OUT/build/host_out.txt"
