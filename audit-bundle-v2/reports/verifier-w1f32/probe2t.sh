#!/usr/bin/env bash
# probe2t: timing test - one Berkeley stream end to end
set -u
W=/c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify-f32
S=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w1f32
export PATH=/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH
PY=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
export MSF_TESTFLOAT_GEN=C:/Users/logan/source/repos/Muse-Softfloat/scratch/oracles/TestFloat-3e/build/Linux-x86_64-GCC/testfloat_gen.exe
cd "$W" || exit 9
mkdir -p "$S/berkeley/vecs"
time "$PY" tests/berkeley_ingest.py --fn f32_add --rm te --level 1 --take 0 --out "$S/berkeley/vecs/timing.vec"
time "$S/msf_runner.exe" verify "$S/berkeley/vecs/timing.vec" > "$S/berkeley/vecs/timing.verify.log" 2>&1
echo "verify exit=$?"
tail -n 6 "$S/berkeley/vecs/timing.verify.log"
