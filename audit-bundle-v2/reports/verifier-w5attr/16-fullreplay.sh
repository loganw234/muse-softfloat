#!/usr/bin/env bash
# 16-fullreplay.sh - replay EVERY committed vector file with our own
# scratch runner; per-file pass/fail census.
set -u
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
V="$SCRATCH"
mkdir -p "$V/tmp/full"
export TMPDIR="$V/tmp" TMP="$V/tmp" TEMP="$V/tmp"
R="$V/tmp/self/runner.exe"
[ -x "$R" ] || { echo "no runner; run 10 first"; exit 2; }
pass=0; fail=0
for f in "$COPY"/tests/vectors/*.vec; do
  b=$(basename "$f")
  "$R" verify "$f" > "$V/tmp/full/$b.log" 2>&1
  rc=$?
  line=$(grep -E "^total" "$V/tmp/full/$b.log" | head -n 1)
  if [ $rc -eq 0 ]; then st=PASS; pass=$((pass+1)); else st=FAIL; fail=$((fail+1)); fi
  echo "$st $b :: $line"
done
echo "files: pass=$pass fail=$fail"
