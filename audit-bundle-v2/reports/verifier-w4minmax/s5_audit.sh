#!/usr/bin/env bash
# verifier-w4minmax s5: independent audit - xcheck my ref vs copy
# generator, my-ref gate vectors through the runner, cell coverage.
set -u
COPY=/c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify4-minmax
SCR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w4minmax
export MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
OUT=$SCR/out-audit
mkdir -p "$OUT"
cd "$COPY" || exit 9
R=build/smoke/msf_runner.exe
echo "== xcheck payload f16 full space: my ref vs copy generator =="
"$MSF_PYTHON" "$SCR/vref.py" xcheck-payload-f16 "$COPY"
echo "== xcheck minmax class cells: my ref vs copy generator =="
"$MSF_PYTHON" "$SCR/vref.py" xcheck-minmax-cells "$COPY"
echo "== my-ref gate vectors =="
"$MSF_PYTHON" "$SCR/vref.py" gate-payload-f16 "$OUT/audit-payload-f16.vec"
"$MSF_PYTHON" "$SCR/vref.py" gate-minmax-sample "$OUT/audit-minmax-sample.vec"
"$MSF_PYTHON" "$SCR/vref.py" gate-seeded "$OUT/audit-seeded.vec" 2000
echo "== replay my-ref gates (isolates C bugs) =="
"$R" verify "$OUT/audit-payload-f16.vec" > "$OUT/audit-payload-replay.log" 2>&1
echo "audit_payload_rc=$? $(grep -E '^total' "$OUT/audit-payload-replay.log")"
grep '^FAIL' "$OUT/audit-payload-replay.log" | sed 's/.*| //' | awk '{print $1}' | sort | uniq -c
"$R" verify "$OUT/audit-minmax-sample.vec" > "$OUT/audit-minmax-replay.log" 2>&1
echo "audit_minmax_rc=$? $(grep -E '^total' "$OUT/audit-minmax-replay.log")"
grep '^FAIL' "$OUT/audit-minmax-replay.log" | sed 's/.*| //' | awk '{print $1}' | sort | uniq -c | head -20
"$R" verify "$OUT/audit-seeded.vec" > "$OUT/audit-seeded-replay.log" 2>&1
echo "audit_seeded_rc=$? $(grep -E '^total' "$OUT/audit-seeded-replay.log")"
grep '^FAIL' "$OUT/audit-seeded-replay.log" | sed 's/.*| //' | awk '{print $1}' | sort | uniq -c | head -20
echo "== committed-vector class-cell coverage =="
"$MSF_PYTHON" "$SCR/vref.py" cell-coverage tests/vectors/minmax-f16.vec
echo "== directed NaN-payload directedness =="
grep -c '7f55\|ff55\|fd55\|7dff\|fc01\|7c01' tests/vectors/minmax-f16.vec
exit 0
