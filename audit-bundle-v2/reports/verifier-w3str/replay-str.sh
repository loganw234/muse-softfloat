#!/usr/bin/env bash
# replay committed str vectors through the probe runner.
R=/c/Users/logan/source/repos/Muse-Softfloat
export TMPDIR=$R/scratch/verifier-w3str/tmp
export TMP="C:\Users\logan\source\repos\Muse-Softfloat\scratch\verifier-w3str\tmp"
export TEMP="$TMP"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
cd "$R/worktrees/verify3-str" || exit 9
"$R/scratch/verifier-w3str/runner.exe" verify \
  tests/vectors/from-decimal-str.vec tests/vectors/from-hex-str.vec \
  tests/vectors/to-decimal-str.vec tests/vectors/to-hex-str.vec \
  > "$R/scratch/verifier-w3str/replay-str.log" 2>&1
echo "exit=$?"
grep -E '^(file|total|VERDICT)' "$R/scratch/verifier-w3str/replay-str.log"
