#!/usr/bin/env bash
# verifier second-attempt: symbol scan mirror over -Os target objects.
set -u
cd /mnt/c/Users/logan/source/repos/Muse-Softfloat
O=scratch/verifier-w5exp2/smoke
NM="/mnt/c/Program Files (x86)/Arm GNU Toolchain arm-none-eabi/14.2 rel1/bin/arm-none-eabi-nm.exe"
"$NM" -u "$O"/arm-Os/*.o > "$O/arm-undefined.txt" 2>/dev/null
sort -u "$O/arm-undefined.txt" | grep -E ' [A-Za-z_]' > "$O/arm-undefined-sorted.txt" || true
echo "target undefined symbols ($(wc -l < "$O/arm-undefined-sorted.txt")):"
cat "$O/arm-undefined-sorted.txt"
if grep -Eq '__aeabi_[fd]|__add[sd]f3|__sub[sd]f3|__mul[sd]f3|__div[sd]f3|__truncdfsf2|__extendsfdf2|__float|__fix|__unord|malloc|free|printf' "$O/arm-undefined-sorted.txt"; then
  echo "SYMBOL SCAN: refused helper symbol"
else
  echo "symbol scan: clean"
fi
