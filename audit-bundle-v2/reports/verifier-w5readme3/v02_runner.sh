#!/usr/bin/env bash
# v02_runner.sh - build host runner in scratch (copy read-only), verify
# committed vectors, print runner totals. No writes to the copy.
set -u
ROOT="$PWD"
V="$ROOT/worktrees/verify5-readme3"
B="$ROOT/scratch/verifier-w5readme3/build"
export PATH=/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH
mkdir -p "$B/tmp"
export TMPDIR="$B/tmp" TMP="$B/tmp" TEMP="$B/tmp"
export MSF_PYTHON="$ROOT/.venv/Scripts/python.exe"
SRC="src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c src/msf_string.c src/msf_math.c src/msf_alg.c src/msf_aug.c"
cd "$V"
# shellcheck disable=SC2086
gcc -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off $SRC tests/runner.c tests/sha256.c -o "$B/msf_runner.exe" > "$B/build.log" 2>&1 || { echo "BUILD FAIL"; tail -20 "$B/build.log"; exit 1; }
echo "runner built"
VECS="tests/vectors/encodings-f16.vec tests/vectors/encodings-f32.vec tests/vectors/encodings-f64.vec tests/vectors/copysign.vec tests/vectors/pack64.vec tests/vectors/pack32.vec tests/vectors/pack16.vec tests/vectors/arith-f32.vec tests/vectors/fma-sqrt-f32.vec tests/vectors/conv-int-f32.vec tests/vectors/toint-f32.vec tests/vectors/rint-misc-f32.vec tests/vectors/compare-f32.vec tests/vectors/arith-f64.vec tests/vectors/conv-f64.vec tests/vectors/misc-f64.vec tests/vectors/compare-f64.vec tests/vectors/nan-f64.vec tests/vectors/arith-f16.vec tests/vectors/fma-sqrt-f16.vec tests/vectors/conv-int-f16.vec tests/vectors/toint-f16.vec tests/vectors/rint-misc-f16.vec tests/vectors/compare-f16.vec tests/vectors/arith-xf.vec tests/vectors/fma-sqrt-xf.vec tests/vectors/conv-xf.vec tests/vectors/compare-xf.vec tests/vectors/traps-xf.vec tests/vectors/from-decimal-str.vec tests/vectors/from-hex-str.vec tests/vectors/to-decimal-str.vec tests/vectors/to-hex-str.vec tests/vectors/minmax-f16.vec tests/vectors/minmax-f32.vec tests/vectors/minmax-f64.vec tests/vectors/payload-f16.vec tests/vectors/payload-f32.vec tests/vectors/payload-f64.vec tests/vectors/trig-f16.vec tests/vectors/trig-f32.vec tests/vectors/trig-f64.vec tests/vectors/alg-f16.vec tests/vectors/alg-f32.vec tests/vectors/alg-f64.vec tests/vectors/explog-f16.vec tests/vectors/explog-f32.vec tests/vectors/explog-f64.vec tests/vectors/aug-f16.vec tests/vectors/aug-f32.vec tests/vectors/aug-f64.vec"
# shellcheck disable=SC2086
"$B/msf_runner.exe" verify $VECS > "$B/verify.log" 2>&1
echo "runner exit: $?"
grep -E '^(total|VERDICT)' "$B/verify.log" | tail -5
grep -c '^file ' "$B/verify.log" || true
tail -3 "$B/verify.log"
