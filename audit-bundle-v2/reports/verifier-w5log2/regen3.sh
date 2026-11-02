#!/usr/bin/env bash
# regen3.sh - vector generator twice; vs committed; Step-3a prefix check.
set -u
export PATH=/c/msys64/mingw64/bin:$PATH
SCR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w5log2
COPY=/c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify5-log2
PY=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
ulimit -v 4194304
cd "$COPY" || exit 9
export MSF_EXPLOG_DECIDER="$SCR/build/own_exhaustive.exe"
rm -rf "$SCR/build/vecA" "$SCR/build/vecB"
"$PY" tests/gen_vectors_explog.py "$SCR/build/vecA" > "$SCR/logs/vecA.log" 2>&1
echo "vecA rc=$?"
tail -3 "$SCR/logs/vecA.log"
"$PY" tests/gen_vectors_explog.py "$SCR/build/vecB" > "$SCR/logs/vecB.log" 2>&1
echo "vecB rc=$?"
tail -3 "$SCR/logs/vecB.log"
for f in explog-f16.vec explog-f32.vec explog-f64.vec; do
  if cmp -s "$SCR/build/vecA/$f" "$SCR/build/vecB/$f"; then echo "TWICE-SAME $f"; else echo "TWICE-DIFF $f"; fi
  if cmp -s "$SCR/build/vecA/$f" tests/vectors/$f; then echo "VS-COMMIT-SAME $f"; else echo "VS-COMMIT-DIFF $f"; fi
done
echo "--- Step-3a exp-line byte-prefix vs parent 54ac1bb:"
for f in explog-f16.vec explog-f32.vec explog-f64.vec; do
  git show "54ac1bb:tests/vectors/$f" > "$SCR/build/parent_$f" 2>/dev/null
  echo "$f parent_lines=$(wc -l < "$SCR/build/parent_$f") regen_lines=$(wc -l < "$SCR/build/vecA/$f")"
done
