#!/bin/bash
# Probe S2: symbol scan over copy ARM objects (run.sh shape).
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
V=$ROOT/scratch/verifier-w4trig
NM="/c/Program Files (x86)/Arm GNU Toolchain arm-none-eabi/14.2 rel1/bin/arm-none-eabi-nm"
cd "$ROOT" || exit 9
find $V/fwbuild -name '*msf*.obj' | grep -v aeabi | grep -v wrap | head -20
"$NM" -u $(find $V/fwbuild -name '*.obj' | grep 'msf_core') 2>/dev/null | sort -u | grep -E ' [A-Za-z_]' > $V/out/arm-undefined.txt || true
cat $V/out/arm-undefined.txt
echo "=== refused-helper check ==="
if grep -Eq '__aeabi_[fd]|__add[sd]f3|__sub[sd]f3|__mul[sd]f3|__div[sd]f3|__truncdfsf2|__extendsfdf2|__float|__fix|__unord|malloc|free|printf' $V/out/arm-undefined.txt; then
  echo "DIRTY"
else
  echo "symbol scan: clean (modulo missing msf_math.o)"
fi
