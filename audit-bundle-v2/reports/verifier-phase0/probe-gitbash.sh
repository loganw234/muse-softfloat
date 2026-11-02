#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 1
mkdir -p scratch/verifier-phase0/tmp
export TMPDIR=$PWD/scratch/verifier-phase0/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\verifier-phase0\tmp'
export TEMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\verifier-phase0\tmp'
echo "=== date / tz ==="
date '+%Y-%m-%d %H:%M:%S %z %A'
echo "=== pwd ==="
pwd
echo "=== python resolution ==="
command -v python || echo "python: NOT FOUND"
python --version 2>&1 || echo "python --version failed rc=$?"
command -v python3 || echo "python3: NOT FOUND"
echo "=== tool versions ==="
git --version 2>&1
command -v arm-none-eabi-gcc || echo "arm-none-eabi-gcc: NOT FOUND in PATH"
arm-none-eabi-gcc --version 2>&1 | head -n 2
command -v gcc || echo "gcc: NOT FOUND"
gcc --version 2>&1 | head -n 2
command -v cmake || echo "cmake: NOT FOUND"
cmake --version 2>&1 | head -n 2
command -v picotool || echo "picotool: NOT FOUND in PATH"
picotool version 2>&1 | head -n 3
command -v openocd || echo "openocd: NOT FOUND"
command -v gh || echo "gh: NOT FOUND"
gh auth status 2>&1 | head -n 8
command -v ffmpeg || echo "ffmpeg: NOT FOUND in PATH"
ffmpeg -version 2>&1 | head -n 1
command -v ninja || echo "ninja(system): NOT FOUND in PATH"
echo "=== PICO_SDK_PATH ==="
echo "PICO_SDK_PATH=${PICO_SDK_PATH:-UNSET}"
echo "=== zip hash ==="
sha256sum softfloat-bootstrap-kit-v1.zip 2>&1
echo "=== kit gate (Git Bash, Miniconda python -I) ==="
ls softfloat-bootstrap-kit/tools
(cd softfloat-bootstrap-kit && python -I tools/check_kit.py; echo "check_kit rc=$?") 2>&1 | tail -n 30
echo "=== ledger.sh selftest ==="
bash softfloat-bootstrap-kit/tools/ledger.sh selftest 2>&1 | tail -n 5
echo "ledger selftest rc above"
echo "=== round_metrics selftest ==="
python -I softfloat-bootstrap-kit/tools/round_metrics.py selftest 2>&1 | tail -n 5
echo "=== plant.py selftest ==="
python -I softfloat-bootstrap-kit/tools/plant.py selftest 2>&1 | tail -n 8
echo "=== DONE probe-gitbash ==="
