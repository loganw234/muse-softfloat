#!/usr/bin/env bash
# s_regenreplay.sh - replay regenerated (current-generator) directed files
set -u
cd "C:/Users/logan/source/repos/Muse-Softfloat/worktrees/verify2-f16" || exit 9
SC="C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w2f16"
R="build/smoke/msf_runner.exe"
for f in "$SC"/regen/*.vec; do
  b=$(basename "$f")
  line=$("$R" verify "$f" 2>&1 | grep -E '^(total|VERDICT)' | tr '\n' ' ')
  echo "regen-$b $line"
done
