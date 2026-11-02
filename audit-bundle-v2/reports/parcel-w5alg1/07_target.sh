#!/usr/bin/env bash
# 07_target.sh - RP2040 target-compile evidence for msf_alg.c:
# clean cortex-m0plus compile (as run.sh symbol_scan does),
# text/data/bss sizes, undefined symbols, -fstack-usage frames.
# Measurement only; no performance claim, no flashing.
set -u
WS=/c/Users/logan/source/repos/Muse-Softfloat
cd "$WS/worktrees/w5-alg1" || exit 9
S="$WS/scratch/parcel-w5alg1"
mkdir -p "$S/out/target" "$S/tmp"
export TMPDIR="$S/tmp"
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-w5alg1\tmp'
export TEMP="$TMP"
export MSF_PYTHON="$WS/.venv/Scripts/python.exe"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
ARM=arm-none-eabi-gcc
command -v $ARM >/dev/null 2>&1 || { echo "TARGET: SKIP-BY-NAME $ARM not found"; exit 0; }
$ARM --version | head -1

$ARM -std=c11 -Os -Wall -Wextra -Werror -mcpu=cortex-m0plus -mthumb \
  -ffreestanding -fstack-usage -c src/msf_alg.c \
  -o "$S/out/target/msf_alg.o" > "$S/out/target/build.log" 2>&1
echo "target build rc=$?"; cat "$S/out/target/build.log"

echo "-- size (text data bss):"
arm-none-eabi-size "$S/out/target/msf_alg.o" | tee "$S/out/target/size.log"
echo "-- undefined symbols:"
arm-none-eabi-nm -u "$S/out/target/msf_alg.o" | tee "$S/out/target/nm.log"
echo "-- stack usage (bytes, static):"
cat src/msf_alg.su 2>/dev/null || cat "$S/out/target/msf_alg.su" 2>/dev/null \
  || ls *.su "$S/out/target/"*.su 2>/dev/null || echo "no .su emitted (see build log)"
# -fstack-usage writes next to the -o object with some drivers,
# next to the source with others; collect whichever this is.
for su in src/msf_alg.su ./msf_alg.su "$S/out/target/msf_alg.su"; do
  if [ -f "$su" ]; then cp "$su" "$S/out/target/msf_alg.su.txt"; echo "stack file: $su"; cat "$su"; fi
done
echo "===== 07_target done ====="
