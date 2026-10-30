#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat/muse-softfloat || exit 9
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
PICO_SDK_PATH="/c/Users/logan/pico/pico-sdk"
BOARD_BUILD=build/board-fw
export TMPDIR=$PWD/$BOARD_BUILD/tmp
mkdir -p "$TMPDIR"
export TMP="$(cygpath -w "$TMPDIR")" TEMP="$(cygpath -w "$TMPDIR")"
echo "cmake: $(which cmake) $(cmake --version | head -1)"
echo "arm gcc: $(which arm-none-eabi-gcc)"
rm -rf "$BOARD_BUILD/fw"
cmake -S board -B "$BOARD_BUILD/fw" -G Ninja -DCMAKE_MAKE_PROGRAM="$(cygpath -w ../.venv/Scripts/ninja.exe | tr '\\' '/')" -DPICO_SDK_PATH="$PICO_SDK_PATH" -DCMAKE_BUILD_TYPE=Release > "$BOARD_BUILD/fw-cmake.log" 2>&1
echo "cmake rc=$?"; tail -15 "$BOARD_BUILD/fw-cmake.log"
cmake --build "$BOARD_BUILD/fw" > "$BOARD_BUILD/fw-build.log" 2>&1
echo "build rc=$?"; tail -25 "$BOARD_BUILD/fw-build.log"
ls -la "$BOARD_BUILD/fw/"*.uf2 2>/dev/null
