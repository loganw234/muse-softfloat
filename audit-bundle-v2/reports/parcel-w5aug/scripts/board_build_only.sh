#!/usr/bin/env bash
# Build (never flash) the harness firmware to prove the
# board CMake + harness pair-reply wiring compiles/links.
set -u
source "$(dirname "$0")/env.sh"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
PICO_SDK_PATH="${PICO_SDK_PATH:-/c/Users/logan/pico/pico-sdk}"
NINJA="$(cygpath -w "$WS/.venv/Scripts/ninja.exe" 2>/dev/null | tr '\\' '/' || echo "$WS/.venv/Scripts/ninja.exe")"
DIR="build/aug-fw"
mkdir -p "$DIR/tmp"
export TMPDIR="$PWD/$DIR/tmp"
export TMP="$(cygpath -w "$TMPDIR" 2>/dev/null || echo "$TMPDIR")"
export TEMP="$TMP"
echo "sdk=$PICO_SDK_PATH ninja=$NINJA"
cmake -S board -B "$DIR/fw" -G Ninja -DCMAKE_MAKE_PROGRAM="$NINJA" \
  -DPICO_SDK_PATH="$PICO_SDK_PATH" -DCMAKE_BUILD_TYPE=Release \
  > "$WS/scratch/parcel-w5aug/logs/board-cmake.log" 2>&1
rc=$?
echo "cmake rc=$rc"
if [ $rc -ne 0 ]; then tail -20 "$WS/scratch/parcel-w5aug/logs/board-cmake.log"; exit $rc; fi
cmake --build "$DIR/fw" --target msf_board_harness \
  > "$WS/scratch/parcel-w5aug/logs/board-build.log" 2>&1
rc=$?
echo "build rc=$rc"
tail -5 "$WS/scratch/parcel-w5aug/logs/board-build.log"
if [ $rc -eq 0 ]; then
  sha256sum "$DIR/fw/msf_board_harness.uf2" "$DIR/fw/msf_board_harness.elf" \
    > "$WS/scratch/parcel-w5aug/logs/board-artifacts.sha"
  cat "$WS/scratch/parcel-w5aug/logs/board-artifacts.sha"
fi
exit $rc
