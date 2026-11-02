#!/usr/bin/env bash
# 08_gates.sh - smoke + standard on the parcel tree; target sizes.
set -u
ulimit -v 4194304 || echo "ulimit -v unsupported here (recorded)"
WS=/c/Users/logan/source/repos/Muse-Softfloat
cd "$WS/worktrees/w5-alg2" || exit 9
S="$WS/scratch/parcel-w5alg2"
mkdir -p "$S/out" "$S/tmp"
export TMPDIR="$S/tmp"
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-w5alg2\tmp'
export TEMP="$TMP"
export MSF_PYTHON="$WS/.venv/Scripts/python.exe"

echo "===== tools/run.sh smoke ====="
time bash tools/run.sh smoke > "$S/out/smoke.log" 2>&1; echo "smoke rc=$?"
cat "$S/out/smoke.log"

echo "===== tools/run.sh standard ====="
time bash tools/run.sh standard > "$S/out/standard.log" 2>&1; echo "standard rc=$?"
tail -40 "$S/out/standard.log"

echo "===== target object sizes (from smoke build/arm) ====="
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
for B in build/smoke build/standard; do
  if [ -f "$B/arm/msf_alg.o" ]; then
    echo "-- $B/arm/msf_alg.o:"
    arm-none-eabi-size "$B/arm/msf_alg.o"
    arm-none-eabi-objdump -h "$B/arm/msf_alg.o" | grep -E 'text|Idx' | head -8
    break
  fi
done
echo "===== hypot symbols in target object ====="
arm-none-eabi-nm build/smoke/arm/msf_alg.o 2>/dev/null | grep -i hypot || true
echo "===== 08_gates done ====="
