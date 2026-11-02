#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat/scratch/oracles || exit 9
unzip -q -o SoftFloat-3e.zip && unzip -q -o TestFloat-3e.zip
echo "unzip rc=$?"
ls
echo ---
ls SoftFloat-3e
echo ---
ls SoftFloat-3e/build
echo ---
ls TestFloat-3e
echo ---
ls TestFloat-3e/build
echo ---
sha256sum SoftFloat-3e/COPYING.txt TestFloat-3e/COPYING.txt
echo ---
cat SoftFloat-3e/build/Linux-x86_64-GCC/Makefile | head -40
echo ---
grep -rn "detectTininess\|tininess" SoftFloat-3e/source/8086-SSE/specialize.h | head
echo ---
cat SoftFloat-3e/source/include/softfloat_types.h | head -30
