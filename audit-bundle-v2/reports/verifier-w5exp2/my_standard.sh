#!/usr/bin/env bash
# verifier second-attempt: standard-only extras (tier1 f16-exhaustive +
# pack-sweep generation, then runner verify). Outputs to scratch.
set -u
cd /mnt/c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify5-exp2
R=/mnt/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w5exp2/smoke/msf_runner.exe
O=/mnt/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w5exp2/smoke
python3 tests/gen_vectors.py f16-exhaustive "$O/f16-exhaustive.vec" > "$O/gen-f16.log" 2>&1 || exit 1
python3 tests/gen_vectors.py pack-sweep "$O/pack-sweep.vec" 200000 > "$O/gen-sweep.log" 2>&1 || exit 1
grep -h . "$O/gen-f16.log" "$O/gen-sweep.log" | grep -E 'wrote|dropped'
"$R" verify "$O/f16-exhaustive.vec" "$O/pack-sweep.vec" > "$O/verify-standard.log" 2>&1
echo "standard-extra RC=$?"
grep -E '^(file|prov|total|VERDICT)' "$O/verify-standard.log"
grep -E '^FAIL' "$O/verify-standard.log" | head -10
