#!/usr/bin/env bash
# verifier-w4minmax s4a: copy-generator gate modes (payload exhaustive
# attempt + seeded sweep) and standard budget.
set -u
COPY=/c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify4-minmax
SCR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w4minmax
export MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
OUT=$SCR/out-gate
mkdir -p "$OUT"
cd "$COPY" || exit 9
R=build/smoke/msf_runner.exe
echo "== copy-generator payload-f16-exhaustive attempt =="
"$MSF_PYTHON" tests/gen_vectors_tier2.py payload-f16-exhaustive "$OUT/copy-payload-f16.vec" > "$OUT/copy-payload-gen.log" 2>&1
echo "payload_exhaustive_rc=$?"
tail -5 "$OUT/copy-payload-gen.log"
echo "== copy-generator seeded N=2000 =="
"$MSF_PYTHON" tests/gen_vectors_tier2.py seeded "$OUT/copy-seeded.vec" 2000 > "$OUT/copy-seeded-gen.log" 2>&1
echo "seeded_rc=$?"
cat "$OUT/copy-seeded-gen.log"
"$R" verify "$OUT/copy-seeded.vec" > "$OUT/copy-seeded-replay.log" 2>&1
echo "seeded_replay_rc=$?"
grep -E '^(total|VERDICT)' "$OUT/copy-seeded-replay.log"
echo "seeded fails by op:"
grep '^FAIL' "$OUT/copy-seeded-replay.log" | sed 's/.*| //' | awk '{print $1}' | sort | uniq -c | sort -rn | head -20
exit 0
