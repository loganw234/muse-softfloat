#!/usr/bin/env bash
# 09_final.sh - post-commit confirmation on the committed tree:
# tools/run.sh standard + vector/table regeneration drift proof.
set -u
ulimit -v 2097152 || echo "ulimit -v unsupported here (recorded)"
WS=/c/Users/logan/source/repos/Muse-Softfloat
cd "$WS/worktrees/w5-alg1" || exit 9
S="$WS/scratch/parcel-w5alg1"
mkdir -p "$S/out" "$S/tmp"
export TMPDIR="$S/tmp"
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-w5alg1\tmp'
export TEMP="$TMP"
export MSF_PYTHON="$WS/.venv/Scripts/python.exe"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
PY="$MSF_PYTHON"
export MSF_ALG_DECIDER="$S/out/alg_decider.exe"
git status --short | tee "$S/out/final_status.log"
git log --oneline -3 | tee -a "$S/out/final_status.log"

echo "===== standard (committed tree) ====="
bash tools/run.sh standard > "$S/out/standard_final.log" 2>&1; echo "standard rc=$?"
grep -E 'inventory:|total |VERDICT|PASS|FAIL' "$S/out/standard_final.log"
tail -2 "$S/out/standard_final.log"

echo "===== regeneration drift proof (must leave tree clean) ====="
"$PY" tools/gen_tables.py > "$S/out/gen_final.log" 2>&1; echo "gen_tables rc=$?"
cat "$S/out/gen_final.log"
"$PY" tests/gen_vectors_alg.py tests/vectors > "$S/out/gen_alg_final.log" 2>&1; echo "gen_alg rc=$?"
cat "$S/out/gen_alg_final.log"
if [ -z "$(git status --porcelain)" ]; then
  echo "DRIFT PROOF: tree clean after full regeneration"
else
  echo "DRIFT PROOF: FAIL"; git status --short
fi
echo "===== 09_final done ====="
