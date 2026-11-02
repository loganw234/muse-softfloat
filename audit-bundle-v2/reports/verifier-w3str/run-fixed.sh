#!/usr/bin/env bash
# Run adversary + slice sets through the fixed-TU diagnostic runner.
R=/c/Users/logan/source/repos/Muse-Softfloat
export TMPDIR=$R/scratch/verifier-w3str/tmp
export TMP="C:\Users\logan\source\repos\Muse-Softfloat\scratch\verifier-w3str\tmp"
export TEMP="$TMP"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
cd "$R/scratch/verifier-w3str" || exit 9
FX="$R/scratch/verifier-w3str/fixed/runner-fixed.exe"
"$FX" verify adv/vw-adv-dec.vec adv/vw-adv-hex.vec adv/vw-adv-todec.vec adv/vw-adv-tohex.vec mpfrslice/vw-mpfr-slice.vec > fixed/adv-slice.log 2>&1
echo "exit=$?"
grep -E '^(file|total|VERDICT)' fixed/adv-slice.log
grep '^FAIL' fixed/adv-slice.log | head -10
echo "=== regular-runner adv classification:"
echo "total adv fails: $(grep -c '^FAIL' adv.log)"
echo "snan: $(grep '^FAIL' adv.log | grep -ci 'snan')"
echo "hexfrac: $(grep '^FAIL' adv.log | grep -c 'from_hex.*IN=[^ ]*\. ')"
echo "other:"
grep '^FAIL' adv.log | grep -vi 'snan' | grep -v 'from_hex.*IN=[^ ]*\. ' | cut -c1-150 | head -20
