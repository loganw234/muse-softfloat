#!/usr/bin/env bash
# Target compile: ARM cortex-m0plus at BOTH -Os and -O3 with
# -Werror (the -O3 pass is the named lesson from the previous
# parcel's maybe-uninitialized slip), plus host -O3, sizes.
set -u
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w5-exp2
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
ARM=arm-none-eabi-gcc
SRC="src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c src/msf_string.c src/msf_math.c src/msf_alg.c"
mkdir -p build/explog/armOs build/explog/armO3 build/explog/hostO3
fail=0
for opt in Os O3; do
    for f in $SRC; do
        $ARM -std=c11 -$opt -Wall -Wextra -Werror -mcpu=cortex-m0plus -mthumb -ffreestanding \
            -c "$f" -o "build/explog/arm$opt/$(basename "$f" .c).o" >> build/explog/target.log 2>&1 \
            || { echo "ARM -$opt FAIL: $f"; fail=1; }
    done
    echo "ARM -$opt clean (all $(echo $SRC | wc -w) TUs)"
    ${ARM%gcc}size build/explog/arm$opt/msf_math.o
done
for f in $SRC; do
    gcc -std=c11 -O3 -Wall -Wextra -Werror -ffp-contract=off \
        -c "$f" -o "build/explog/hostO3/$(basename "$f" .c).o" >> build/explog/target.log 2>&1 \
        || { echo "HOST -O3 FAIL: $f"; fail=1; }
done
echo "HOST -O3 clean"
gcc -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off \
    -c src/msf_math.c -o build/explog/hostO3/msf_math-O2.o >> build/explog/target.log 2>&1 \
    || { echo "HOST -O2 FAIL"; fail=1; }
echo "HOST -O2 clean"
size build/explog/hostO3/msf_math.o build/explog/hostO3/msf_math-O2.o
# undefined-symbol hygiene on both ARM objects sets
for opt in Os O3; do
    ${ARM%gcc}nm -u build/explog/arm$opt/*.o | sort -u | grep -E ' [A-Za-z_]' > build/explog/arm$opt-undefined.txt || true
    if grep -Eq '__aeabi_[fd]|__add[sd]f3|__sub[sd]f3|__mul[sd]f3|__div[sd]f3|__truncdfsf2|__extendsfdf2|__float|__fix|__unord|malloc|free|printf' build/explog/arm$opt-undefined.txt; then
        echo "SYMBOL SCAN FAIL at -$opt"; fail=1
    else
        echo "symbol scan clean at -$opt ($(wc -l < build/explog/arm$opt-undefined.txt) undefined)"
        cat build/explog/arm$opt-undefined.txt
    fi
done
[ "$fail" -eq 0 ] && echo "TARGET: PASS" || echo "TARGET: FAIL"
exit "$fail"
