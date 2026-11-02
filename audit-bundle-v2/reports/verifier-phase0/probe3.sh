#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 1
mkdir -p scratch/verifier-phase0/tmp
export TMPDIR=$PWD/scratch/verifier-phase0/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\verifier-phase0\tmp'
export TEMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\verifier-phase0\tmp'
echo "=== .venv python ==="
.venv/Scripts/python.exe --version 2>&1
echo "=== .venv packages via import ==="
.venv/Scripts/python.exe -c "import numpy, mpmath, pypdf, PIL, matplotlib, imageio; print('imports OK'); print('numpy', numpy.__version__); print('mpmath', mpmath.__version__); print('pypdf', pypdf.__version__); print('Pillow', PIL.__version__); print('matplotlib', matplotlib.__version__); print('imageio', imageio.__version__)" 2>&1
echo "=== .venv ninja ==="
.venv/Scripts/ninja.exe --version 2>&1
echo "=== imageio-ffmpeg binary ==="
.venv/Scripts/python.exe -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())" 2>&1
echo "=== system ninja execute test ==="
ninja --version 2>&1 || echo "system ninja failed rc=$?"
echo "=== plant.py around 650 ==="
sed -n '640,660p' softfloat-bootstrap-kit/tools/plant.py
echo "=== round_metrics usage ==="
python -I softfloat-bootstrap-kit/tools/round_metrics.py --help 2>&1 | head -n 30
echo "=== round_metrics selftest variants ==="
python -I softfloat-bootstrap-kit/tools/round_metrics.py --selftest 2>&1 | tail -n 5
echo "=== mktemp WITHOUT TMPDIR (AGENTS item 2 probe) ==="
( unset TMPDIR TMP TEMP; mktemp 2>&1 || echo "mktemp-no-tmpdir failed rc=$?" )
echo "=== pico-sdk version hunt (names only) ==="
ls /c/Users/logan/pico/pico-sdk | head -n 20
ls /c/Users/logan/pico/pico-sdk/src/common/pico_base_headers/include/pico/version.h 2>&1
grep -E "PICO_SDK_VERSION_(MAJOR|MINOR|REVISION|STRING)" /c/Users/logan/pico/pico-sdk/src/common/pico_base_headers/include/pico/version.h 2>&1 | head -n 12
cat /c/Users/logan/pico/pico-sdk/.git/HEAD 2>&1 || true
echo "=== kit top-level names (template existence) ==="
ls softfloat-bootstrap-kit
find softfloat-bootstrap-kit -maxdepth 3 -name 'PROJECT.md' -o -maxdepth 3 -name 'OWNER.md' -o -maxdepth 3 -name 'BOARD.md' -o -maxdepth 3 -name 'HARNESS.md' -o -maxdepth 3 -name 'METRICS.md' -o -maxdepth 3 -name 'WORKFLOW.md' 2>/dev/null
echo "=== DONE probe3 ==="
