#!/usr/bin/env bash
# s_exhaust.sh - generate + replay exhaustive unary f16->f16
set -u
cd "C:/Users/logan/source/repos/Muse-Softfloat/worktrees/verify2-f16" || exit 9
SC="C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w2f16"
C:/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe "$SC/gen_exhaust.py" > "$SC/exhaust-gen.log" 2>&1
R="build/smoke/msf_runner.exe"
: > "$SC/exhaust-replay.log"
for f in "$SC"/exh-*.vec; do
  b=$(basename "$f")
  line=$("$R" verify "$f" 2>&1 | grep -E '^(total|VERDICT)' | tr '\n' ' ')
  echo "$b $line" >> "$SC/exhaust-replay.log"
done
cat "$SC/exhaust-replay.log"
