# Board firmware (P0): harness, interposition hello, bench skeleton.
# Built by board/run_board.sh / board/run_bench.sh under the board
# lock; never part of the host gate. SDK glue is included from the
# SDK's own external/ directory - no SDK file is copied or edited
# (SF-0 Sections 3.4, 4.5). Toolchain pins: pico-sdk 2.3.1,
# Arm GNU Toolchain 14.2.1, CMake 4.4.4.
cmake_minimum_required(VERSION 3.13)

if(NOT DEFINED PICO_SDK_PATH AND DEFINED ENV{PICO_SDK_PATH})
    set(PICO_SDK_PATH $ENV{PICO_SDK_PATH})
endif()
if(NOT DEFINED PICO_SDK_PATH)
    message(FATAL_ERROR "PICO_SDK_PATH not set (env or -D)")
endif()
include(${PICO_SDK_PATH}/external/pico_sdk_import.cmake)

project(msf_board C CXX ASM)
pico_sdk_init()

set(MSF_ROOT ${CMAKE_CURRENT_LIST_DIR}/..)
set(MSF_SRC
    ${MSF_ROOT}/src/msf16.c
    ${MSF_ROOT}/src/msf32.c
    ${MSF_ROOT}/src/msf64.c
    ${MSF_ROOT}/src/msf_flags.c
    ${MSF_ROOT}/src/msf_wide.c
    ${MSF_ROOT}/src/msf_roundpack.c)

add_library(msf_core STATIC ${MSF_SRC})
target_include_directories(msf_core PUBLIC ${MSF_ROOT}/include ${MSF_ROOT}/src)
target_compile_options(msf_core PRIVATE -std=c11 -Wall -Wextra -Werror -ffp-contract=off)

add_executable(msf_board_harness harness_main.c ${MSF_ROOT}/tests/sha256.c)
target_include_directories(msf_board_harness PRIVATE ${MSF_ROOT})
target_link_libraries(msf_board_harness msf_core pico_stdlib pico_unique_id)
pico_enable_stdio_usb(msf_board_harness 1)
pico_enable_stdio_uart(msf_board_harness 0)
pico_add_extra_outputs(msf_board_harness)

add_executable(msf_hello hello_main.c ${MSF_ROOT}/compat/msf_wrap.c)
# Our flavour replaces the SDK's for the wrapped names: select the
# empty "compiler" flavour so the SDK's own __wrap_copysign(f) bodies
# are absent, then apply our --wrap (measured duplicate otherwise).
# Wave 3 registers a full flavour library in this same switch shape.
pico_set_float_implementation(msf_hello compiler)
pico_set_double_implementation(msf_hello compiler)
target_include_directories(msf_hello PRIVATE ${MSF_ROOT} ${MSF_ROOT}/compat)
target_compile_definitions(msf_hello PRIVATE MSF_WRAP_SELFTEST)
target_compile_options(msf_hello PRIVATE -fno-builtin-copysign -fno-builtin-copysignf -ffp-contract=off)
# The SDK's own --wrap mechanism (pico_wrap_function shape, S3 1.1),
# applied from this project, not by editing SDK files.
target_link_options(msf_hello PRIVATE "LINKER:--wrap=copysignf" "LINKER:--wrap=copysign")
target_link_libraries(msf_hello msf_core pico_stdlib pico_unique_id pico_multicore)
pico_enable_stdio_usb(msf_hello 1)
pico_enable_stdio_uart(msf_hello 0)
pico_add_extra_outputs(msf_hello)

add_executable(msf_bench bench_main.c)
target_include_directories(msf_bench PRIVATE ${MSF_ROOT})
target_compile_options(msf_bench PRIVATE -ffp-contract=off)
if(DEFINED MSF_BENCH_FLAVOUR)
    pico_set_float_implementation(msf_bench ${MSF_BENCH_FLAVOUR})
    pico_set_double_implementation(msf_bench ${MSF_BENCH_FLAVOUR})
    target_compile_definitions(msf_bench PRIVATE MSF_FLAVOUR_NAME="${MSF_BENCH_FLAVOUR}")
endif()
target_link_libraries(msf_bench msf_core pico_stdlib pico_unique_id)
pico_enable_stdio_usb(msf_bench 1)
pico_enable_stdio_uart(msf_bench 0)
pico_add_extra_outputs(msf_bench)
