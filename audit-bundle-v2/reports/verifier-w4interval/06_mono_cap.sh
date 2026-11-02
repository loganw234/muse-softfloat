#!/usr/bin/env bash
# 06_mono_cap.sh - tolerance-halving monotonicity + op-cap enforcement.
set -u
VROOT="/c/Users/logan/source/repos/Muse-Softfloat"
OUT="$VROOT/scratch/verifier-w4interval"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
EXE="$OUT/build/interval_host.exe"
COPY="$VROOT/worktrees/verify4-interval"
"$EXE" "$COPY/tests/interval_catalogue.tsv" --tol-half > "$OUT/build/host_half.txt" 2>&1
echo "half rc=$?"; tail -2 "$OUT/build/host_half.txt" | cut -c1-160
"$EXE" "$COPY/tests/interval_catalogue.tsv" --cap 100 > "$OUT/build/host_cap100.txt" 2>&1
echo "cap100 rc=$?"; tail -2 "$OUT/build/host_cap100.txt" | cut -c1-160
grep -c "caphit=1" "$OUT/build/host_cap100.txt"
grep -c "kind=torus" "$OUT/build/host_cap100.txt"
