#!/usr/bin/env bash
# 08-control.sh - watch the new te/ta control refuse by breaking it in
# scratch: the committed control 3b text always reports ok; demonstrate
# with a fixed awk (proper || control_bad) that swap is caught, and that
# the committed text cannot refuse.
set -u
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
V="$SCRATCH"
mkdir -p "$V/tmp/ctrl"
export TMPDIR="$V/tmp" TMP="$V/tmp" TEMP="$V/tmp"
/c/msys64/mingw64/bin/gcc -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off \
  -I"$COPY/include" -I"$COPY/src" -I"$COPY/tests" \
  "$COPY"/src/*.c "$COPY/tests/runner.c" "$COPY/tests/sha256.c" \
  -o "$V/tmp/ctrl/runner.exe" 2>"$V/tmp/ctrl/build.log" || { cat "$V/tmp/ctrl/build.log"; exit 1; }
echo "== committed control 3b text =="
grep -n -A5 "wrongrm-ta" "$COPY/tools/run.sh"
echo "== run the swap with our own runner =="
awk '{if($2=="te")$2="ta"; else if($2=="ta")$2="te"} {print}' \
  "$COPY/tests/vectors/arith-f32.vec" > "$V/tmp/ctrl/wrongrm-ta.vec"
"$V/tmp/ctrl/runner.exe" verify "$V/tmp/ctrl/wrongrm-ta.vec" > "$V/tmp/ctrl/swap.log" 2>&1
echo "swap exit: $?"
grep -E "^(total|VERDICT)" "$V/tmp/ctrl/swap.log" | head
grep -c "^FAIL" "$V/tmp/ctrl/swap.log"
echo "== unswapped file must PASS (control sanity) =="
"$V/tmp/ctrl/runner.exe" verify "$COPY/tests/vectors/arith-f32.vec" > "$V/tmp/ctrl/plain.log" 2>&1
echo "plain exit: $?"
grep -E "^(total|VERDICT)" "$V/tmp/ctrl/plain.log" | head
