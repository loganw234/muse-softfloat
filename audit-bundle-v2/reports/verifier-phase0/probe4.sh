#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 1
mkdir -p scratch/verifier-phase0/tmp scratch/verifier-phase0/build
export TMPDIR=$PWD/scratch/verifier-phase0/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\verifier-phase0\tmp'
export TEMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\verifier-phase0\tmp'
echo "=== plant.py line 650 exact ==="
grep -n 're.search.*key' softfloat-bootstrap-kit/tools/plant.py | head -n 6
sed -n '650p' softfloat-bootstrap-kit/tools/plant.py
echo "=== host gcc compile+run ==="
gcc scratch/verifier-phase0/hello.c -o scratch/verifier-phase0/build/hello-host.exe 2>&1 && scratch/verifier-phase0/build/hello-host.exe
echo "=== arm gcc compile (no run on x86 host) ==="
arm-none-eabi-gcc -mcpu=cortex-m0plus -c scratch/verifier-phase0/hello.c -o scratch/verifier-phase0/build/hello-arm.o 2>&1 && file scratch/verifier-phase0/build/hello-arm.o
echo "=== WinGet packages names (ffmpeg presence) ==="
ls "/c/Users/logan/AppData/Local/Microsoft/WinGet/Packages" 2>&1
echo "=== ls-remote origin (push state) ==="
git -c safe.directory=C:/Users/logan/source/repos/Muse-Softfloat/muse-softfloat -C muse-softfloat ls-remote origin 2>&1 | head -n 10
echo "ls-remote done"
echo "=== DONE probe4 ==="
