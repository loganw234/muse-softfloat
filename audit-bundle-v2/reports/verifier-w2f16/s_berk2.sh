#!/usr/bin/env bash
# s_berk2.sh - Level-2 takes: add/mul/sqrt te+tz x2M
set -u
CP="C:/Users/logan/source/repos/Muse-Softfloat/worktrees/verify2-f16"
SC="C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w2f16"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export MSF_TESTFLOAT_GEN="C:/Users/logan/source/repos/Muse-Softfloat/scratch/oracles/TestFloat-3e/build/Linux-x86_64-GCC/testfloat_gen.exe"
export MSF_PYTHON="C:/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe"
cd "$CP" || exit 9
R="build/smoke/msf_runner.exe"
for spec in "f16_add te" "f16_add tz" "f16_mul te" "f16_mul tz" "f16_sqrt te" "f16_sqrt tz"; do
  set -- $spec
  fn="$1"; rm="$2"
  tag="${fn}-${rm}-l2take"
  out="$SC/berk1/${tag}.vec"
  "$MSF_PYTHON" tests/berkeley_ingest.py --fn "$fn" --rm "$rm" --level 2 --take 2000000 --out "$out" >> "$SC/berk1-ingest.log" 2>&1
  n=$(grep -vc '^#' "$out")
  res=$("$R" verify "$out" 2>&1 | grep -E '^(total|VERDICT)' | tr '\n' ' ')
  echo "$tag n=$n $res"
done
echo ALLDONE2
