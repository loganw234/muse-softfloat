#!/usr/bin/env bash
# fullsurf.sh - runner over the full committed vector surface
# (same VECS list as tools/run.sh), no manifest gate, verdict only.
set -u
export PATH=/c/msys64/mingw64/bin:$PATH
SCR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w5log2
COPY=/c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify5-log2
ulimit -v 4194304
cd "$SCR" || exit 9
VECS=""
for v in encodings-f16 encodings-f32 encodings-f64 copysign pack64 pack32 pack16 arith-f32 fma-sqrt-f32 conv-int-f32 toint-f32 rint-misc-f32 compare-f32 arith-f64 conv-f64 misc-f64 compare-f64 nan-f64 arith-f16 fma-sqrt-f16 conv-int-f16 toint-f16 rint-misc-f16 compare-f16 arith-xf fma-sqrt-xf conv-xf compare-xf traps-xf from-decimal-str from-hex-str to-decimal-str to-hex-str minmax-f16 minmax-f32 minmax-f64 payload-f16 payload-f32 payload-f64 trig-f16 trig-f32 trig-f64 alg-f16 alg-f32 alg-f64 explog-f16 explog-f32 explog-f64; do
  VECS="$VECS $COPY/tests/vectors/$v.vec"
done
# shellcheck disable=SC2086
./build/msf_runner.exe verify $VECS > logs/fullsurf.log 2>&1
echo "rc=$?"
grep -E '^total|VERDICT' logs/fullsurf.log
echo "--- non-explog FAILs:"
grep '^FAIL' logs/fullsurf.log | grep -v 'explog-' | head -10
echo "--- non-explog FAIL count:"
grep '^FAIL' logs/fullsurf.log | grep -v 'explog-' | wc -l
