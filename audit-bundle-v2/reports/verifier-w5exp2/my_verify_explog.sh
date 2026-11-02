#!/usr/bin/env bash
# verifier second-attempt: runner verify of explog vecs, then full VECS.
set -u
cd /mnt/c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify5-exp2
R=/mnt/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w5exp2/smoke/msf_runner.exe
O=/mnt/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w5exp2/smoke
echo "== explog vecs only =="
"$R" verify tests/vectors/explog-f16.vec tests/vectors/explog-f32.vec tests/vectors/explog-f64.vec > "$O/verify-explog.log" 2>&1
echo "explog-verify RC=$?"
grep -E '^(file|prov|total|VERDICT)' "$O/verify-explog.log"
grep -E '^(FAIL|MISMATCH)' "$O/verify-explog.log" | head -20
