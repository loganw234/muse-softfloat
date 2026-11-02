#!/usr/bin/env bash
# run the four 100k fuzz sets through both runners, classify, roundtrip.
R=/c/Users/logan/source/repos/Muse-Softfloat
export TMPDIR=$R/scratch/verifier-w3str/tmp
export TMP="C:\Users\logan\source\repos\Muse-Softfloat\scratch\verifier-w3str\tmp"
export TEMP="$TMP"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
cd "$R/scratch/verifier-w3str" || exit 9
FX=./fixed/runner-fixed.exe
echo "=== regular runner:"
./runner.exe verify fuzz/vw-fuzz-from-dec.vec fuzz/vw-fuzz-from-hex.vec \
  fuzz/vw-fuzz-to-dec.vec fuzz/vw-fuzz-to-hex.vec > fuzz/fuzz.log 2>&1
echo "exit=$?"
grep -E '^(file|total|VERDICT)' fuzz/fuzz.log
echo "=== fixed runner:"
$FX verify fuzz/vw-fuzz-from-dec.vec fuzz/vw-fuzz-from-hex.vec \
  fuzz/vw-fuzz-to-dec.vec fuzz/vw-fuzz-to-hex.vec > fixed/fuzz.log 2>&1
echo "exit=$?"
grep -E '^(file|total|VERDICT)' fixed/fuzz.log
grep '^FAIL' fixed/fuzz.log | head -10
echo "=== regular-runner fail classes:"
F=fuzz/fuzz.log
echo "snan: $(grep '^FAIL' $F | grep -ci 'snan')"
echo "tie-pattern to-dec/beyondh (non-snan, non-from_hex):"
grep '^FAIL' $F | grep -vi 'snan' | grep -v 'from_hex' | wc -l
echo "from_hex non-snan fails: $(grep '^FAIL' $F | grep -vi 'snan' | grep -c 'from_hex')"
echo "from_hex non-snan fails WITHOUT frac digits in IN (expect 0):"
grep '^FAIL' $F | grep -vi 'snan' | grep 'from_hex' | grep -vc 'IN=[^ ]*\.'
echo "to_hex / other fails (expect 0):"
grep '^FAIL' $F | grep -vi 'snan' | grep -v 'from_hex' | grep -vc 'to_decimal\|from_decimal'
