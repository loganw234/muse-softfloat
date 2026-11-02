#!/usr/bin/env bash
# s_exhtriage.sh - triage exhaustive failures: NaN-input vs finite-input
set -u
cd "C:/Users/logan/source/repos/Muse-Softfloat/worktrees/verify2-f16" || exit 9
SC="C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w2f16"
R="build/smoke/msf_runner.exe"
for t in sqrt@te next_up@- round_to_integral_ties_to_even@- round_to_integral_exact@te; do
  "$R" verify "$SC/exh-$t.vec" > "$SC/triage-$t.log" 2>&1
done
echo done-triage
