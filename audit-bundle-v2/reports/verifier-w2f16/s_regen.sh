#!/usr/bin/env bash
# s_regen.sh - regenerate directed f16 vectors, byte-compare
set -u
CP="C:/Users/logan/source/repos/Muse-Softfloat/worktrees/verify2-f16"
SC="C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w2f16"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export MSF_PYTHON="C:/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe"
cd "$CP" || exit 9
mkdir -p "$SC/regen"
"$MSF_PYTHON" tests/gen_vectors_f16.py directed "$SC/regen" > "$SC/regen-gen.log" 2>&1
echo "gen-exit=$?"
ls "$SC/regen"
for f in "$SC"/regen/*.vec; do
  b=$(basename "$f")
  if cmp -s "$f" "tests/vectors/$b"; then echo "IDENTICAL: $b"; else echo "DIFF: $b"; fi
done
