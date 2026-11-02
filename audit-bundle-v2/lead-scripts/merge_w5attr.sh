#!/usr/bin/env bash
# Merge wave5-attr, land plants rows, run standard gate. Git Bash.
set -u
cd "$(dirname "$0")/../../muse-softfloat" || exit 9
export PATH="/c/Program Files/Git/cmd:/c/Program Files/Git/mingw64/bin:/c/Program Files/Git/usr/bin:/usr/bin:$PATH"
command -v git || { echo "git not on PATH"; exit 1; }
WS="$(cd .. && pwd)"
export MSF_PYTHON="$WS/.venv/Scripts/python.exe"
export TMPDIR="$WS/scratch/lead/tmp" TMP="$WS/scratch/lead/tmp" TEMP="$WS/scratch/lead/tmp"
mkdir -p "$TMPDIR"
[ -z "$(git status --porcelain)" ] || { echo "dirty tree - stop"; exit 1; }

cat > "$TMPDIR/mm.txt" <<'EOF'
Merged SF-2 Step 1: roundTiesToAway, fifth public attribute

Merges wave5-attr (8bfc877). The public enum gains
MSF_ROUND_TIES_TO_AWAY = 4 (the internal mode already in
the pack); the kernel bill is exactly the two string-path
cases the study found (src/msf_string.c dec_round_inc and
the to_hex precision switch - today value 4 silently meant
toward-zero there). Zero new inventory rows; all 255
attribute-carrying rows now carry ties-to-away evidence.

Evidence: 21,858 committed ta lines at directed-mode
volume (decided 10,985; relabeled trig 10,873 under the
no-exact-ties theorems, provenance-tagged); Berkeley
-rnear_maxMag level-1 18,978,288 cases over 51 functions,
flags exact; binary16 five-mode exhaustive streams; a new
te/ta wrong-mode runner control. Two measured corrections
to the study: sqrt no-ties holds for homogeneous/widening
only (33 decided narrowing-tie witnesses added), and
gen_vectors_str.py had four ta-less reference arms, not
three.

Planted-copy verification (verifier-w5attr, Spark): NOT
READY on the planted copy as constructed, 5 of 5 caught
(61 of 65 cumulative), no non-plant defect; the sqrt
narrowing scope was independently re-derived. Board
sampled replay follows on the merge tree.

Co-Authored-By: Muse Code (muse-wonder-full-1.0) <noreply@meta.ai>
EOF
git merge --no-ff wave5-attr -F "$TMPDIR/mm.txt" || exit 1

cat >> docs/metrics/plants.jsonl <<'EOF'
{"wave": "wave5", "verifier": "verifier-w5attr", "work": "SF-2 Step 1: roundTiesToAway fifth attribute", "key_sha256": "c6ac1bec2a4788bda327872373efefe4f2d66caed45023a84706dd547812b12d", "plant": 1, "shape": "decimal ties-to-away drops exact ties", "grade": "caught", "graded_by": "lead", "checked_by": "integration", "note": "(b) dec_round_inc return gt_half: 924+41 committed ta FAILs; own probe 2.5->2e+00 want 3e+00"}
{"wave": "wave5", "verifier": "verifier-w5attr", "work": "SF-2 Step 1: roundTiesToAway fifth attribute", "key_sha256": "c6ac1bec2a4788bda327872373efefe4f2d66caed45023a84706dd547812b12d", "plant": 2, "shape": "public attribute value no longer matches internal mode 4", "grade": "caught", "graded_by": "lead", "checked_by": "integration", "note": "(a) gen_tables emits =5 vs header/internal =4; smoke refuses at drift check"}
{"wave": "wave5", "verifier": "verifier-w5attr", "work": "SF-2 Step 1: roundTiesToAway fifth attribute", "key_sha256": "c6ac1bec2a4788bda327872373efefe4f2d66caed45023a84706dd547812b12d", "plant": 3, "shape": "string reference ties-to-away arm drops ties", "grade": "caught", "graded_by": "lead", "checked_by": "integration", "note": "(a) _round_ratio_to_int 2*r>den: kernel right 0x3c01 vs ref 0x3c00; directed regen crashes"}
{"wave": "wave5", "verifier": "verifier-w5attr", "work": "SF-2 Step 1: roundTiesToAway fifth attribute", "key_sha256": "c6ac1bec2a4788bda327872373efefe4f2d66caed45023a84706dd547812b12d", "plant": 4, "shape": "one relabeled trig flag expectation corrupted", "grade": "caught", "graded_by": "lead", "checked_by": "integration", "note": "(b) trig-f64.vec:8 ta 0 -> 0 01 for 00; sole divergence of 10,873 relabeled lines"}
{"wave": "wave5", "verifier": "verifier-w5attr", "work": "SF-2 Step 1: roundTiesToAway fifth attribute", "key_sha256": "c6ac1bec2a4788bda327872373efefe4f2d66caed45023a84706dd547812b12d", "plant": 5, "shape": "te/ta wrong-mode control can no longer fail", "grade": "caught", "graded_by": "lead", "checked_by": "integration", "note": "(a) run.sh control_ok on both arms; verifier's own swap run caught 106 FAILs"}
EOF

"$MSF_PYTHON" - <<'PYEOF'
import json
n = sum(1 for l in open("docs/metrics/plants.jsonl", encoding="utf-8") if l.strip() and json.loads(l))
print("plants.jsonl OK", n, "rows")
PYEOF
[ $? -eq 0 ] || exit 1

cat > "$TMPDIR/rm.txt" <<'EOF'
Landed verifier-w5attr plant grades (5 of 5)

61 of 65 cumulative; the sqrt narrowing-tie scope was
independently re-derived by the verifier.

Co-Authored-By: Muse Code (muse-wonder-full-1.0) <noreply@meta.ai>
EOF
git add docs/metrics/plants.jsonl && git commit -F "$TMPDIR/rm.txt" || exit 1

echo "--- standard gate on merge tree ---"
bash tools/run.sh standard; rc=$?
echo "standard rc=$rc"
git log --oneline -3
exit $rc
