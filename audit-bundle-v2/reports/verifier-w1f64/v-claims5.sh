#!/usr/bin/env bash
set -uo pipefail
G="C:/Program Files/Git/bin/git.exe"
V=/c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify-f64
echo "===== gen_vectors.py base->copy ====="
"$G" -c safe.directory="$V" -C "$V" diff 4cdb912 -- tests/gen_vectors.py
echo "===== pack64 base->copy (head) ====="
"$G" -c safe.directory="$V" -C "$V" diff 4cdb912 -- tests/vectors/pack64.vec | head -n 20
echo "===== roundpack base->copy stat + lead-fix marker ====="
"$G" -c safe.directory="$V" -C "$V" diff 4cdb912 -- src/msf_roundpack.c | grep -E "^[+-]" | grep -v "^[+-][+-]" | head -n 20
