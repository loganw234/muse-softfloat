#!/usr/bin/env bash
# 07-sqrt.sh - re-derive the no-exact-ties scope: count decided narrowing
# sqrt ta lines; test that relabeling them (te->ta expectation copy)
# would FAIL on exactly those lines.
set -u
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
V="$SCRATCH"
mkdir -p "$V/tmp/sqrt"
export TMPDIR="$V/tmp" TMP="$V/tmp" TEMP="$V/tmp"
/c/msys64/mingw64/bin/gcc -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off \
  -I"$COPY/include" -I"$COPY/src" -I"$COPY/tests" \
  "$COPY"/src/*.c "$COPY/tests/runner.c" "$COPY/tests/sha256.c" \
  -o "$V/tmp/sqrt/runner.exe" 2>"$V/tmp/sqrt/build.log" || { cat "$V/tmp/sqrt/build.log"; exit 1; }
echo "== sqrt ta lines in committed sets =="
grep -h " ta " "$COPY"/tests/vectors/fma-sqrt-*.vec "$COPY"/tests/vectors/arith-*.vec "$COPY"/tests/vectors/conv-*.vec 2>/dev/null | grep -i "sqrt" | tee "$V/tmp/sqrt/sqrt_ta.vec" | wc -l
grep -h " ta " "$COPY"/tests/vectors/*.vec | grep -i "sqrt" > "$V/tmp/sqrt/sqrt_ta.vec"
wc -l < "$V/tmp/sqrt/sqrt_ta.vec"
echo "== narrowing (wider source than dest) sqrt ta lines =="
grep -E "msf(16|32)_sqrt_f(32|64)|msf32_sqrt_f64" "$V/tmp/sqrt/sqrt_ta.vec" | tee "$V/tmp/sqrt/sqrt_narrow_ta.vec" | wc -l
echo "== sample narrowing lines =="
head -n 5 "$V/tmp/sqrt/sqrt_narrow_ta.vec"
echo "== relabel control: te expectations replayed as ta =="
grep -h " te " "$COPY"/tests/vectors/*.vec | grep -iE "msf(16|32)_sqrt_f(32|64)|msf32_sqrt_f64" | head -n 200 > "$V/tmp/sqrt/sqrt_narrow_te.vec"
wc -l < "$V/tmp/sqrt/sqrt_narrow_te.vec"
awk '{if($2=="te")$2="ta"; print}' "$V/tmp/sqrt/sqrt_narrow_te.vec" > "$V/tmp/sqrt/sqrt_narrow_relabel.vec"
"$V/tmp/sqrt/runner.exe" verify "$V/tmp/sqrt/sqrt_narrow_relabel.vec" > "$V/tmp/sqrt/relabel.log" 2>&1
echo "relabel exit: $?"
grep -E "^(total|VERDICT)" "$V/tmp/sqrt/relabel.log" | head
echo "== theorem-scope (homogeneous+widening) relabel =="
grep -h " te " "$COPY"/tests/vectors/*.vec | grep -iE "sqrt" | grep -vE "msf(16|32)_sqrt_f(32|64)|msf32_sqrt_f64" | head -n 272 > "$V/tmp/sqrt/sqrt_wide_te.vec"
wc -l < "$V/tmp/sqrt/sqrt_wide_te.vec"
awk '{if($2=="te")$2="ta"; print}' "$V/tmp/sqrt/sqrt_wide_te.vec" > "$V/tmp/sqrt/sqrt_wide_relabel.vec"
"$V/tmp/sqrt/runner.exe" verify "$V/tmp/sqrt/sqrt_wide_relabel.vec" > "$V/tmp/sqrt/relabel_wide.log" 2>&1
echo "wide relabel exit: $?"
grep -E "^(total|VERDICT)" "$V/tmp/sqrt/relabel_wide.log" | head
