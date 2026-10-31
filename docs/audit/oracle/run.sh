#!/usr/bin/env bash
# Audit oracle (2026-10-31): differential tests of muse-softfloat against
# x86-64 hardware (SSE2/AVX/FMA3/F16C/AVX-512F), glibc 2.39 C23 functions
# and MPFR 4.2. Needs: x86-64 Linux with those CPU features, gcc,
# python3, libmpfr-dev. Run from anywhere: bash docs/audit/oracle/run.sh
set -eu
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../.." && pwd)"
OUT="${OUT:-$ROOT/build/audit-oracle}"
mkdir -p "$OUT"
cd "$OUT"
python3 "$HERE/genwrap.py" > /dev/null
python3 "$HERE/genwrap3.py" > /dev/null
SRC="$ROOT/src/msf16.c $ROOT/src/msf32.c $ROOT/src/msf64.c $ROOT/src/msf_flags.c $ROOT/src/msf_wide.c $ROOT/src/msf_roundpack.c $ROOT/src/msf_string.c $ROOT/src/msf_math.c $ROOT/src/msf_alg.c $ROOT/src/msf_aug.c"
CF="-std=c11 -O2 -ffp-contract=off -mno-fma -I$ROOT/include -I$HERE -I$OUT"
gcc $CF "$HERE/hwdiff.c"  $SRC -lm -o hwdiff
gcc $CF "$HERE/hwdiff2.c" $SRC -lm -o hwdiff2
gcc $CF "$HERE/mpta.c"    $SRC -lmpfr -lgmp -lm -o mpta
gcc $CF -pthread "$HERE/f16exh.c" $SRC -lm -o f16exh
gcc $CF "$HERE/mpt2.c"    $SRC -lmpfr -lgmp -lm -o mpt2
gcc $CF "$HERE/nanrepro.c" $SRC -o nanrepro
gcc $CF "$HERE/rmprobe.c"  $SRC -o rmprobe
gcc $CF "$HERE/strprobe.c" $SRC -o strprobe
# negative control: the tester must fail against a tininess-before-rounding build
gcc $CF -DMSF_TININESS_AFTER_ROUNDING=0 "$HERE/hwdiff.c" $SRC -lm -o hwdiff_mutant
SCALE="${SCALE:-1}"
./hwdiff "$SCALE" 0xC0FFEE > hwdiff.log 2>&1 || { grep -vE '^  NAN-PAYLOAD' hwdiff.log; echo "hwdiff: MISMATCHES"; exit 1; }
grep -vE '^  NAN-PAYLOAD' hwdiff.log
./hwdiff2 "$SCALE" 4242
./mpta 300000 7
./mpt2 $((5000 * SCALE)) 11
if ./hwdiff_mutant 1 > mutant.log 2>&1; then echo "CONTROL NOT REFUSED"; exit 1; else echo "control tininess-before-rounding mutant: refused ($(grep '^TOTAL' mutant.log))"; fi
echo "== L1 repro (sNaN narrowing sign)"; ./nanrepro
echo "== L2 repro (out-of-range rounding values)"; ./rmprobe
echo "== S1/S2 repros (beyond-H input, exponent clamp)"; ./strprobe
# exhaustive binary16 (slow: 11+ min per op on 3 threads, div slowest): set F16EXH=1
if [ "${F16EXH:-0}" = 1 ]; then for op in 0 1 2; do ./f16exh $op 0 3; done; fi
