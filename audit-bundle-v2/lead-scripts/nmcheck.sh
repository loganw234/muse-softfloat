#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat/muse-softfloat || exit 9
arm-none-eabi-nm build/board-fw/fw/msf_hello.elf | grep -i copysign
echo ---
arm-none-eabi-nm build/board-fw/fw/msf_hello.elf | grep -E ' (T|t) (msf32_copy_sign|msf_wrap_state|__wrap_)'
