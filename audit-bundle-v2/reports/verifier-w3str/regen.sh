#!/usr/bin/env bash
# regenerate str vectors to temp and byte-compare with committed copies.
R=/c/Users/logan/source/repos/Muse-Softfloat
export TMPDIR=$R/scratch/verifier-w3str/tmp
export TMP="C:\Users\logan\source\repos\Muse-Softfloat\scratch\verifier-w3str\tmp"
export TEMP="$TMP"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
mkdir -p "$R/scratch/verifier-w3str/regen"
cd "$R/worktrees/verify3-str" || exit 9
PY="$R/.venv/Scripts/python.exe"
"$PY" tests/gen_vectors_str.py directed "$R/scratch/verifier-w3str/regen" \
  > "$R/scratch/verifier-w3str/regen.log" 2>&1
echo "gen exit=$?"
tail -5 "$R/scratch/verifier-w3str/regen.log"
for f in from-decimal-str.vec from-hex-str.vec to-decimal-str.vec to-hex-str.vec; do
  if cmp -s "tests/vectors/$f" "$R/scratch/verifier-w3str/regen/$f"; then
    echo "$f IDENTICAL"
  else
    echo "$f DIFFERS:"
    cmp "tests/vectors/$f" "$R/scratch/verifier-w3str/regen/$f" | head -3
  fi
done
