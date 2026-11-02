#!/bin/bash
# Probe F: self-test mydecider on hand-derived cases.
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
PY=$ROOT/.venv/Scripts/python.exe
cd "$ROOT" || exit 9
cat > scratch/verifier-w4trig/tmp/selftest.in <<'EOF'
msf16_sin_pi 3c00
msf16_sin_pi bc00
msf16_sin_pi 3800
msf16_sin_pi b800
msf16_cos_pi b800
msf16_cos_pi 3800
msf64_sin_pi 3ff0000000000000
msf64_cos_pi bfe0000000000000
msf32_sin_pi 3fc00000
msf64_sin_pi 3ff0000000000001
msf32_cos_pi 33000000
msf16_sin_pi 0001
msf16_cos_pi 0001
EOF
"$PY" scratch/verifier-w4trig/mydecider.py scratch/verifier-w4trig/tmp/selftest.in scratch/verifier-w4trig/tmp/selftest.out
echo "rc=$?"
cat scratch/verifier-w4trig/tmp/selftest.out
