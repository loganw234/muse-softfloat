#!/usr/bin/env bash
# UF2-only build probe for parcel-w6examples (never flashes).
set -u
export MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w6-examples || exit 9
PICO_SDK_PATH="${PICO_SDK_PATH:-/c/Users/logan/pico/pico-sdk}"
NINJA="$(cygpath -w /c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/ninja.exe | tr '\\' '/')"
BUILD=build/example-pico
mkdir -p "$BUILD/tmp"
export TMPDIR=$PWD/$BUILD/tmp
export TMP="$(cygpath -w "$TMPDIR" 2>/dev/null || echo "$TMPDIR")"
export TEMP="$TMP"
echo "cmake: $(command -v cmake) $(cmake --version 2>/dev/null | head -1)"
echo "ninja: $NINJA"
echo "arm gcc: $(arm-none-eabi-gcc --version 2>/dev/null | head -1)"
echo "pico-sdk: $PICO_SDK_PATH"
cmake -S examples/pico -B "$BUILD" -G Ninja -DCMAKE_MAKE_PROGRAM="$NINJA" \
    -DPICO_SDK_PATH="$PICO_SDK_PATH" -DCMAKE_BUILD_TYPE=Release \
    > "$BUILD-cmake.log" 2>&1 \
    || { tail -30 "$BUILD-cmake.log"; echo "PICO CONFIGURE FAIL"; exit 1; }
cmake --build "$BUILD" > "$BUILD-build.log" 2>&1 \
    || { tail -40 "$BUILD-build.log"; echo "PICO BUILD FAIL"; exit 1; }
echo "built firmware in $BUILD"
ls -l "$BUILD/msf_example.uf2" "$BUILD/msf_example.elf"
sha256sum "$BUILD/msf_example.uf2" "$BUILD/msf_example.elf"
grep -iE 'warning|error' "$BUILD-build.log" | head -20 || true
echo "PICO BUILD PASS"
