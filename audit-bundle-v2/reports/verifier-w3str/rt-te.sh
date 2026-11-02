#!/usr/bin/env bash
R=/c/Users/logan/source/repos/Muse-Softfloat
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
cd "$R/scratch/verifier-w3str" || exit 9
"$R/.venv/Scripts/python.exe" vw_roundtrip.py \
  fuzz/vw-fuzz-to-dec.vec fuzz/vw-fuzz-to-hex.vec \
  adv/vw-adv-todec.vec adv/vw-adv-tohex.vec 2>&1 | grep -v 'RT-DIR' | head -30
