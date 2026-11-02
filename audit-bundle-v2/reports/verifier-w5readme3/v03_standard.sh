#!/usr/bin/env bash
# v03_standard.sh - regenerate standard extras to scratch, verify with runner.
set -u
ROOT="$PWD"
V="$ROOT/worktrees/verify5-readme3"
B="$ROOT/scratch/verifier-w5readme3/build"
export PATH=/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH
mkdir -p "$B/tmp"
export TMPDIR="$B/tmp" TMP="$B/tmp" TEMP="$B/tmp"
export MSF_PYTHON="$ROOT/.venv/Scripts/python.exe"
cd "$V"
"$MSF_PYTHON" tests/gen_vectors.py f16-exhaustive "$B/f16-exhaustive.vec" > "$B/gen-f16.log" 2>&1 || { echo "GEN F16 FAIL"; tail -5 "$B/gen-f16.log"; exit 1; }
"$MSF_PYTHON" tests/gen_vectors.py pack-sweep "$B/pack-sweep.vec" 200000 > "$B/gen-sweep.log" 2>&1 || { echo "GEN SWEEP FAIL"; tail -5 "$B/gen-sweep.log"; exit 1; }
grep -h . "$B/gen-f16.log" "$B/gen-sweep.log" | grep -E 'wrote|dropped' || cat "$B/gen-f16.log" "$B/gen-sweep.log"
wc -l "$B/f16-exhaustive.vec" "$B/pack-sweep.vec"
"$B/msf_runner.exe" verify "$B/f16-exhaustive.vec" "$B/pack-sweep.vec" > "$B/verify-standard.log" 2>&1
echo "runner exit: $?"
grep -E '^(total|VERDICT)' "$B/verify-standard.log" | tail -3
