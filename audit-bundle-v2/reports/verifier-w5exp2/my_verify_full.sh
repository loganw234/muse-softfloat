#!/usr/bin/env bash
# verifier second-attempt: full VECS verify with manifest + expect-counts.
set -u
cd /mnt/c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify5-exp2
R=/mnt/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w5exp2/smoke/msf_runner.exe
O=/mnt/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w5exp2/smoke
VECS="tests/vectors/encodings-f16.vec tests/vectors/encodings-f32.vec tests/vectors/encodings-f64.vec tests/vectors/copysign.vec tests/vectors/pack64.vec tests/vectors/pack32.vec tests/vectors/pack16.vec tests/vectors/arith-f32.vec tests/vectors/fma-sqrt-f32.vec tests/vectors/conv-int-f32.vec tests/vectors/toint-f32.vec tests/vectors/rint-misc-f32.vec tests/vectors/compare-f32.vec tests/vectors/arith-f64.vec tests/vectors/conv-f64.vec tests/vectors/misc-f64.vec tests/vectors/compare-f64.vec tests/vectors/nan-f64.vec tests/vectors/arith-f16.vec tests/vectors/fma-sqrt-f16.vec tests/vectors/conv-int-f16.vec tests/vectors/toint-f16.vec tests/vectors/rint-misc-f16.vec tests/vectors/compare-f16.vec tests/vectors/arith-xf.vec tests/vectors/fma-sqrt-xf.vec tests/vectors/conv-xf.vec tests/vectors/compare-xf.vec tests/vectors/traps-xf.vec tests/vectors/from-decimal-str.vec tests/vectors/from-hex-str.vec tests/vectors/to-decimal-str.vec tests/vectors/to-hex-str.vec tests/vectors/minmax-f16.vec tests/vectors/minmax-f32.vec tests/vectors/minmax-f64.vec tests/vectors/payload-f16.vec tests/vectors/payload-f32.vec tests/vectors/payload-f64.vec tests/vectors/trig-f16.vec tests/vectors/trig-f32.vec tests/vectors/trig-f64.vec tests/vectors/alg-f16.vec tests/vectors/alg-f32.vec tests/vectors/alg-f64.vec tests/vectors/explog-f16.vec tests/vectors/explog-f32.vec tests/vectors/explog-f64.vec"
sha256sum $VECS > "$O/manifest.txt"
awk '!/^#/ && NF>0 {print $NF}' $VECS | sort | uniq -c | awk '{print $2, $1}' > "$O/expect.txt"
"$R" verify --manifest "$O/manifest.txt" --expect-counts "$O/expect.txt" $VECS > "$O/verify.log" 2>&1
echo "full-verify RC=$?"
grep -E '^(total|VERDICT|manifest)' "$O/verify.log"
grep -E '^FAIL' "$O/verify.log" | head -20
