#!/usr/bin/env bash
# prefix.sh - Step-3a exp-line byte-prefix vs parent 54ac1bb.
set -u
export PATH=/c/msys64/mingw64/bin:$PATH
SCR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w5log2
COPY=/c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify5-log2
cd "$COPY" || exit 9
for f in explog-f16.vec explog-f32.vec explog-f64.vec; do
  git show "54ac1bb:tests/vectors/$f" > "$SCR/build/par_$f" 2>/dev/null
  n=$(wc -l < "$SCR/build/par_$f")
  if head -n "$n" "tests/vectors/$f" | cmp -s - "$SCR/build/par_$f"; then
    echo "PREFIX-SAME $f ($n lines)"
  else
    echo "PREFIX-DIFF $f ($n lines)"
    head -n "$n" "tests/vectors/$f" | diff - "$SCR/build/par_$f" | head -6
  fi
done
