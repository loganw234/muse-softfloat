#!/bin/bash
# Probe H5: hand-decided deep-saturation cases vs harness decide.
# Expectations derived by exact delta inequalities (no oracle):
#  f64 cos(2^-1074): d=(pi*2^-1074)^2/2 << ulp(1)/2 -> te/tp:1.0/10,
#    tz/tn:0x3FEFFFFFFFFFFFFF/10
#  f64 cos(2^-30): d~2^-61.3 -> te/tp:1.0/10, tz/tn:0x3FEFFFFFFFFFFFFF/10
#  f64 cos(2^-60): d~2^-121 -> same pattern as 2^-30
#  f32 cos(2^-149): d~2^-299 -> te/tp:0x3F800000/10, tz/tn:0x3F7FFFFF/10
#  f16 cos(0x0001): cross-check vs mydecider (d~2^-51, decided there)
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
V=$ROOT/scratch/verifier-w4trig
cd "$ROOT" || exit 9
cat > $V/tmp/sat.in <<'EOF'
msf64_cos_pi 1
msf64_cos_pi 10000000000000
msf64_cos_pi 3e30000000000000
msf32_cos_pi 1
msf16_cos_pi 1
EOF
$V/tmp/trigx.exe decide < $V/tmp/sat.in
echo "--- hand expectations ---"
echo "msf64_cos_pi 1: te/tp 3ff0000000000000/10, tz/tn 3fefffffffffffff/10"
echo "msf64_cos_pi 10000000000000 (2^-1022): te/tp 3ff0000000000000/10, tz/tn 3fefffffffffffff/10"
echo "msf64_cos_pi 3e30000000000000 (2^-60): te/tp 3ff0000000000000/10, tz/tn 3fefffffffffffff/10"
echo "msf32_cos_pi 1: te/tp 3f800000/10, tz/tn 3f7fffff/10"
echo "msf16_cos_pi 1: te/tp 3c00/10, tz/tn 3bff/10"
grep -E 'msf(16_cos_pi 1|32_cos_pi 1|64_cos_pi (1|10000000000000|3e30000000000000)) ' $V/tmp/xdec.my.out
