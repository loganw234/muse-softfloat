#!/usr/bin/env bash
# arm-check.sh - compile-only portability probe of the changed
# workload core for the board target. No board script is run,
# nothing is flashed; this is a compiler invocation in scratch.
set -u
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
WS=/c/Users/logan/source/repos/Muse-Softfloat
SCR=$WS/scratch/parcel-w6augint
mkdir -p "$SCR/build" "$SCR/tmp"
export TMPDIR=$SCR/tmp
export TMP="$(cygpath -w "$SCR/tmp")"
export TEMP="$TMP"
if ! command -v arm-none-eabi-gcc >/dev/null 2>&1; then
    echo "arm-check: SKIP-BY-NAME arm-none-eabi-gcc not on PATH"
    exit 0
fi
arm-none-eabi-gcc --version | head -1
arm-none-eabi-gcc -std=c11 -Os -Wall -Wextra -Werror -mcpu=cortex-m0plus -mthumb -ffreestanding -ffp-contract=off -c board/interval_workload.c -o "$SCR/build/interval_workload-arm.o" > "$SCR/build/arm-check.log" 2>&1 || { cat "$SCR/build/arm-check.log"; echo "ARM COMPILE FAILED"; exit 1; }
${ARM_NM:-arm-none-eabi-nm} -u "$SCR/build/interval_workload-arm.o" | sort -u > "$SCR/build/arm-undefined.txt" || true
echo "undefined symbols referenced by interval_workload.o:"
cat "$SCR/build/arm-undefined.txt"
ls -l "$SCR/build/interval_workload-arm.o"
echo "arm-check: PASS"
