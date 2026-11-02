#!/usr/bin/env bash
# standard-tail arithmetic coverage via probe runner (no project build).
R=/c/Users/logan/source/repos/Muse-Softfloat
export TMPDIR=$R/scratch/verifier-w3str/tmp
export TMP="C:\Users\logan\source\repos\Muse-Softfloat\scratch\verifier-w3str\tmp"
export TEMP="$TMP"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
cd "$R/worktrees/verify3-str" || exit 9
PY="$R/.venv/Scripts/python.exe"
mkdir -p "$R/scratch/verifier-w3str/std"
"$PY" tests/gen_vectors.py f16-exhaustive "$R/scratch/verifier-w3str/std/f16-exhaustive.vec" > "$R/scratch/verifier-w3str/std/gen-f16.log" 2>&1
echo "f16 gen exit=$?"
"$PY" tests/gen_vectors.py pack-sweep "$R/scratch/verifier-w3str/std/pack-sweep.vec" 200000 > "$R/scratch/verifier-w3str/std/gen-sweep.log" 2>&1
echo "sweep gen exit=$?"
grep -h . "$R/scratch/verifier-w3str/std/gen-f16.log" "$R/scratch/verifier-w3str/std/gen-sweep.log" | grep -E 'wrote|dropped'
"$R/scratch/verifier-w3str/runner.exe" verify "$R/scratch/verifier-w3str/std/f16-exhaustive.vec" "$R/scratch/verifier-w3str/std/pack-sweep.vec" > "$R/scratch/verifier-w3str/std/verify.log" 2>&1
echo "verify exit=$?"
grep -E '^(file|total|VERDICT)' "$R/scratch/verifier-w3str/std/verify.log"
