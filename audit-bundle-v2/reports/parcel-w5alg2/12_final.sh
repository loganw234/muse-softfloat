#!/usr/bin/env bash
# 12_final.sh - post-commit: full regeneration leaves the
# committed tree clean; smoke + standard re-run.
set -u
ulimit -v 4194304 || echo "ulimit -v unsupported here (recorded)"
WS=/c/Users/logan/source/repos/Muse-Softfloat
cd "$WS/worktrees/w5-alg2" || exit 9
S="$WS/scratch/parcel-w5alg2"
mkdir -p "$S/out" "$S/tmp"
export TMPDIR="$S/tmp"
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-w5alg2\tmp'
export TEMP="$TMP"
export MSF_PYTHON="$WS/.venv/Scripts/python.exe"
export MSF_ALG_DECIDER="$S/out/alg_decider.exe"
git log --oneline -3
git status --porcelain; echo "pre-regen status above"

"$MSF_PYTHON" tools/gen_tables.py > "$S/out/final_regen_tables.log" 2>&1; echo "tables rc=$?"
"$MSF_PYTHON" tests/gen_vectors_alg.py tests/vectors > "$S/out/final_regen_vec.log" 2>&1; echo "vectors rc=$?"
cat "$S/out/final_regen_vec.log"
echo "post-regen status (must be empty):"
git status --porcelain

bash tools/run.sh smoke > "$S/out/final_smoke.log" 2>&1; echo "smoke rc=$?"
grep -E 'total|VERDICT|inventory:|budget' "$S/out/final_smoke.log"
bash tools/run.sh standard > "$S/out/final_standard.log" 2>&1; echo "standard rc=$?"
grep -E 'total|VERDICT|inventory:|budget' "$S/out/final_standard.log"
git status --porcelain; echo "final status above (empty = clean)"
git diff --stat HEAD~2 HEAD | tail -3
