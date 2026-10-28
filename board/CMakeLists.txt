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
    ${MSF_ROOT}/src/msf_roundpack.c
    ${MSF_ROOT}/src/msf_string.c
    ${MSF_ROOT}/src/msf_math.c)

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

# ---- AEABI compat surface + IAS15 workload firmware ----------------
# SF-0 Sec.3.4 layer 1 over the gated core (compat/msf_aeabi.c),
# selected the same way as the P0 hello: empty "compiler" flavour so
# no SDK double body is present, then our --wrap for every binary64
# helper the compiler emits. The IAS15 workload itself is GPL and
# lives outside this repository; point IAS15_EXTRACT_DIR at its
# extract tree (scratch/ias15/extract in the workspace) to build
# msf_ias15. msf_aeabi_selftest has no workload dependency and
# always builds.
set(MSF_AEABI_WRAP_SYMBOLS
    __aeabi_dadd __aeabi_dsub __aeabi_drsub __aeabi_dmul __aeabi_ddiv
    __aeabi_dneg __aeabi_dcmpeq __aeabi_dcmplt __aeabi_dcmple
    __aeabi_dcmpgt __aeabi_dcmpge __aeabi_dcmpun
    __aeabi_i2d __aeabi_ui2d __aeabi_l2d __aeabi_ul2d
    __aeabi_d2iz __aeabi_d2uiz __aeabi_d2lz __aeabi_d2ulz
    __aeabi_f2d __aeabi_d2f
    sqrt fabs fma copysignf copysign
    # named traps (compat/msf_aeabi.c): the upstream tree's
    # never-executed libm surface; any call stops loudly.
    acos acosh asin atan cbrt cos cosh exp floor log log10
    sin sinh tan tanh atan2 pow fmod)
set(MSF_AEABI_SRC
    ${MSF_ROOT}/compat/msf_aeabi.c
    ${MSF_ROOT}/compat/msf_wrap.c
    ${MSF_ROOT}/board/ias15_trap.c)

function(msf_aeabi_target_wraps tgt)
    pico_set_float_implementation(${tgt} compiler)
    pico_set_double_implementation(${tgt} compiler)
    foreach(sym IN LISTS MSF_AEABI_WRAP_SYMBOLS)
        target_link_options(${tgt} PRIVATE "LINKER:--wrap=${sym}")
    endforeach()
endfunction()

add_executable(msf_aeabi_selftest aeabi_selftest_main.c ias15_selftest.c
               ${MSF_AEABI_SRC})
msf_aeabi_target_wraps(msf_aeabi_selftest)
target_compile_definitions(msf_aeabi_selftest PRIVATE PICO_STACK_SIZE=0x1000)
target_include_directories(msf_aeabi_selftest PRIVATE ${CMAKE_CURRENT_LIST_DIR} ${MSF_ROOT} ${MSF_ROOT}/compat)
target_compile_options(msf_aeabi_selftest PRIVATE -ffp-contract=off -fno-fast-math)
set_source_files_properties(${MSF_AEABI_SRC} PROPERTIES
    COMPILE_OPTIONS "-ffp-contract=off")
set_source_files_properties(ias15_selftest.c PROPERTIES COMPILE_OPTIONS
    "-fno-builtin-sqrt;-fno-builtin-fabs;-fno-builtin-copysign")
target_link_libraries(msf_aeabi_selftest msf_core pico_stdlib pico_unique_id)
pico_enable_stdio_usb(msf_aeabi_selftest 1)
pico_enable_stdio_uart(msf_aeabi_selftest 0)
pico_add_extra_outputs(msf_aeabi_selftest)

if(DEFINED IAS15_EXTRACT_DIR)
    set(IAS15X_SRC
        ${IAS15_EXTRACT_DIR}/integrator_ias15_min.c
        ${IAS15_EXTRACT_DIR}/gravity_basic_min.c
        ${IAS15_EXTRACT_DIR}/sim_min.c
        ${IAS15_EXTRACT_DIR}/ias15x.c)
    add_executable(msf_ias15 ias15_main.c ias15_selftest.c ias15_hash.c
                   ${MSF_ROOT}/tests/sha256.c ${MSF_AEABI_SRC} ${IAS15X_SRC})
    msf_aeabi_target_wraps(msf_ias15)
    # Stack measured with -fstack-usage: ias15 step 816 B + gravity
    # 288 B + core/IRQ depth exceeds comfort on the 2 KiB default.
    target_compile_definitions(msf_ias15 PRIVATE PICO_STACK_SIZE=0x1000)
    target_include_directories(msf_ias15 PRIVATE ${CMAKE_CURRENT_LIST_DIR}
                               ${MSF_ROOT} ${MSF_ROOT}/compat
                               ${IAS15_EXTRACT_DIR})
    target_compile_options(msf_ias15 PRIVATE -ffp-contract=off -fno-fast-math)
    # Workload TUs: pinned like the desktop reference in every flag
    # that exists on both sides (SF-0 Sec.9). No fast-math family,
    # no contraction, sqrt stays a call to the wrapped helper.
    set_source_files_properties(${IAS15X_SRC} PROPERTIES COMPILE_OPTIONS
        "-std=c99;-O2;-ffp-contract=off;-fno-fast-math;-fno-unsafe-math-optimizations;-fno-builtin-sqrt;-DREB_MIN_NMAX=16;-DREB_MIN_NO_MALLOC")
    target_link_libraries(msf_ias15 msf_core pico_stdlib pico_unique_id)
    pico_enable_stdio_usb(msf_ias15 1)
    pico_enable_stdio_uart(msf_ias15 0)
    pico_add_extra_outputs(msf_ias15)
else()
    message(STATUS "msf_ias15 skipped: -DIAS15_EXTRACT_DIR=<extract tree> not given")
endif()

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

# ---- Step 1c interval workload firmware (SF-1) -------------------
# Streams the frozen catalogue from the host and must reproduce
# the IW1 host SHA-256 bit-for-bit (interval_main.c header). The
# workload core calls the public API directly, so no AEABI wraps
# are needed; stack is 4 KiB (SCRATCH_Y bound, as msf_ias15)
# for the torus bisection + stage-3 distillation frames over
# the static context.
add_executable(msf_interval interval_main.c interval_workload.c
               ${MSF_ROOT}/tests/sha256.c)
target_compile_definitions(msf_interval PRIVATE PICO_STACK_SIZE=0x1000)
target_include_directories(msf_interval PRIVATE ${CMAKE_CURRENT_LIST_DIR} ${MSF_ROOT})
target_compile_options(msf_interval PRIVATE -ffp-contract=off -fno-fast-math)
target_link_libraries(msf_interval msf_core pico_stdlib pico_unique_id)
pico_enable_stdio_usb(msf_interval 1)
pico_enable_stdio_uart(msf_interval 0)
pico_add_extra_outputs(msf_interval)
