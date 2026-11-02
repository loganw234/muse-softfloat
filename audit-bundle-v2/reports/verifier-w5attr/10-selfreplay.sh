#!/usr/bin/env bash
# 10-selfreplay.sh - replay the copy's own committed string vectors with
# our own scratch-built runner; count ta-line failures (the kernel bug
# must show here if the committed expectations are decided).
set -u
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
V="$SCRATCH"
mkdir -p "$V/tmp/self"
export TMPDIR="$V/tmp" TMP="$V/tmp" TEMP="$V/tmp"
/c/msys64/mingw64/bin/gcc -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off \
  -I"$COPY/include" -I"$COPY/src" -I"$COPY/tests" \
  "$COPY"/src/*.c "$COPY/tests/runner.c" "$COPY/tests/sha256.c" \
  -o "$V/tmp/self/runner.exe" 2>"$V/tmp/self/build.log" || { cat "$V/tmp/self/build.log"; exit 1; }
for f in to-decimal-str from-decimal-str to-hex-str from-hex-str; do
  "$V/tmp/self/runner.exe" verify "$COPY/tests/vectors/$f.vec" > "$V/tmp/self/$f.log" 2>&1
  echo "$f exit: $?"
  grep -E "^(total|VERDICT)" "$V/tmp/self/$f.log" | head -n 3
  echo "FAIL lines total: $(grep -c "^FAIL" "$V/tmp/self/$f.log" || true)"
  echo "FAIL lines with ta mode: $(grep "^FAIL" "$V/tmp/self/$f.log" | grep -c " ta " || true)"
done
echo "== first ta FAILs =="
grep -h "^FAIL" "$V/tmp/self/"*.log | grep " ta " | head -n 8
