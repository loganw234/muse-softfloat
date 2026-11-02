#!/bin/bash
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
command -v cmake
cmake --version 2>/dev/null | head -1
command -v ninja
command -v arm-none-eabi-gcc
ls -d /c/pico-sdk* /c/Users/logan/pico-sdk* /opt/pico-sdk* 2>/dev/null
echo "PICO_SDK_PATH=$PICO_SDK_PATH"
ls "$PICO_SDK_PATH/external/pico_sdk_import.cmake" 2>/dev/null
