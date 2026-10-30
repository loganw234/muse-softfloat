# Minimal Pico SDK project for the on-ramp example, in the
# board/ shape (see board/CMakeLists.txt): SDK glue comes
# from the SDK's own external/ directory, the library builds
# as one static target from src/, and the single firmware
# prints over USB CDC. Unlike board/'s workload firmwares no
# compatibility wrappers are needed - main.c calls the
# public API directly, exactly as on the host.
# Toolchain pins match board/: pico-sdk 2.3.1,
# Arm GNU Toolchain 14.2.1, CMake 4.4.4.
cmake_minimum_required(VERSION 3.13)

if(NOT DEFINED PICO_SDK_PATH AND DEFINED ENV{PICO_SDK_PATH})
    set(PICO_SDK_PATH $ENV{PICO_SDK_PATH})
endif()
if(NOT DEFINED PICO_SDK_PATH)
    message(FATAL_ERROR "PICO_SDK_PATH not set (env or -D)")
endif()
include(${PICO_SDK_PATH}/external/pico_sdk_import.cmake)

project(msf_example C CXX ASM)
pico_sdk_init()

set(MSF_ROOT ${CMAKE_CURRENT_LIST_DIR}/../..)
set(MSF_SRC
    ${MSF_ROOT}/src/msf16.c
    ${MSF_ROOT}/src/msf32.c
    ${MSF_ROOT}/src/msf64.c
    ${MSF_ROOT}/src/msf_flags.c
    ${MSF_ROOT}/src/msf_wide.c
    ${MSF_ROOT}/src/msf_roundpack.c
    ${MSF_ROOT}/src/msf_string.c
    ${MSF_ROOT}/src/msf_math.c
    ${MSF_ROOT}/src/msf_alg.c
    ${MSF_ROOT}/src/msf_aug.c)

add_library(msf_core STATIC ${MSF_SRC})
target_include_directories(msf_core PUBLIC ${MSF_ROOT}/include ${MSF_ROOT}/src)
target_compile_options(msf_core PRIVATE -std=c11 -Wall -Wextra -Werror -ffp-contract=off)

add_executable(msf_example main.c)
target_compile_options(msf_example PRIVATE -ffp-contract=off)
target_link_libraries(msf_example msf_core pico_stdlib pico_unique_id)
pico_enable_stdio_usb(msf_example 1)
pico_enable_stdio_uart(msf_example 0)
pico_add_extra_outputs(msf_example)
