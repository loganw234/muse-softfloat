#!/usr/bin/env bash
# 09-trigrelabel.sh - replay the relabeled trig file(s) and one flipped
# expectation of our own making as a control.
set -u
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
V="$SCRATCH"
mkdir -p "$V/tmp/trig"
export TMPDIR="$V/tmp" TMP="$V/tmp" TEMP="$V/tmp"
/c/msys64/mingw64/bin/gcc -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off \
  -I"$COPY/include" -I"$COPY/src" -I"$COPY/tests" \
  "$COPY"/src/*.c "$COPY/tests/runner.c" "$COPY/tests/sha256.c" \
  -o "$V/tmp/trig/runner.exe" 2>"$V/tmp/trig/build.log" || { cat "$V/tmp/trig/build.log"; exit 1; }
echo "== relabeled trig ta lines committed =="
grep -h "ta-relabel" "$COPY"/tests/vectors/trig-*.vec | wc -l
grep -h " ta " "$COPY"/tests/vectors/trig-*.vec | grep -vc "ta-relabel" || true
echo "== replay all committed trig files =="
"$V/tmp/trig/runner.exe" verify "$COPY"/tests/vectors/trig-f16.vec "$COPY"/tests/vectors/trig-f32.vec "$COPY"/tests/vectors/trig-f64.vec > "$V/tmp/trig/replay.log" 2>&1
echo "replay exit: $?"
grep -E "^(total|VERDICT)" "$V/tmp/trig/replay.log" | head
echo "== flipped-expectation control (must FAIL 1 line) =="
head -n 50 "$COPY/tests/vectors/trig-f32.vec" > "$V/tmp/trig/flip_src.vec"
awk 'BEGIN{d=0} !/^#/ && NF>0 && !d {for(i=1;i<=NF;i++) if($i=="->") {$(i+1)=($(i+1)=="0"?"1":"0"); d=1}} {print}' "$V/tmp/trig/flip_src.vec" > "$V/tmp/trig/flip.vec"
"$V/tmp/trig/runner.exe" verify "$V/tmp/trig/flip.vec" > "$V/tmp/trig/flip.log" 2>&1
echo "flip exit: $?"
grep -E "^(total|VERDICT)" "$V/tmp/trig/flip.log" | head
grep -c "^FAIL" "$V/tmp/trig/flip.log" || true
