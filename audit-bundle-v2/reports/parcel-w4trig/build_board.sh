#!/usr/bin/env bash
# Compile-only firmware build (brief: no flashing, no board.lock).
set -u
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w4-trig
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
[ -n "${PICO_SDK_PATH:-}" ] || PICO_SDK_PATH="/c/Users/logan/pico/pico-sdk"
NINJA="$(cygpath -w /c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/ninja.exe | tr '\\' '/')"
DIR=build/board-trig
export TMPDIR=$PWD/$DIR/tmp
mkdir -p "$TMPDIR"
export TMP="$(cygpath -w "$TMPDIR" 2>/dev/null || echo "$TMPDIR")"
export TEMP="$TMP"
O=/c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w4trig/out
which cmake || echo "cmake not on PATH"
cmake -S board -B "$DIR" -G Ninja -DCMAKE_MAKE_PROGRAM="$NINJA" \
    -DPICO_SDK_PATH="$PICO_SDK_PATH" -DCMAKE_BUILD_TYPE=Release \
    > "$O/board_cmake.log" 2>&1
echo "configure rc=$?"
START=$(date +%s)
cmake --build "$DIR" > "$O/board_build.log" 2>&1
echo "build rc=$? in $(( $(date +%s) - START ))s"
tail -5 "$O/board_build.log"
ls "$DIR"/*.uf2 "$DIR"/*.elf 2>/dev/null
arm-none-eabi-size "$DIR"/CMakeFiles/msf_core.dir/*.obj 2>/dev/null | grep -E "msf_math|text" || \
  find "$DIR" -name "msf_math*" | head -5
for uf2 in "$DIR"/*.uf2; do
  [ -f "$uf2" ] && sha256sum "$uf2"
done
