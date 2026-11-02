#!/usr/bin/env bash
# probe1b: regen drift - gen_tables to temp (byte-compare 4 outputs),
# gen_vectors_f32 directed to temp (diff vs committed).
set -u
W=/c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify-f32
S=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w1f32
export PATH=/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH
PY=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
export MSF_TESTFLOAT_GEN=C:/Users/logan/source/repos/Muse-Softfloat/scratch/oracles/TestFloat-3e/build/Linux-x86_64-GCC/testfloat_gen.exe
cd "$W" || exit 9
R="$S/regen-check"
rm -rf "$R"
mkdir -p "$R/tables" "$R/vecs"
{
echo "=== gen_tables regen ==="
"$PY" tools/gen_tables.py "$R/tables" > "$R/gen-tables.log" 2>&1
echo "gen_tables exit=$?"
for f in include/muse_softfloat.h src/msf_formats.h tests/msf_dispatch.h docs/COVERAGE.tsv; do
  base=$(basename "$f")
  found=""
  for cand in "$R/tables/$f" "$R/tables/$base" "$R/tables/"*; do
    [ -n "$found" ] && break
    [ -f "$cand" ] && found="$cand"
  done
  echo "-- $f -> check $found"
  if [ -n "$found" ] && [ -f "$found" ]; then
    if cmp -s "$f" "$found"; then echo "IDENTICAL $f"; else echo "DRIFT $f"; fi
  fi
done
echo "--- gen-check tree ---"
find "$R/tables" -type f | head -n 20
echo "=== gen_vectors_f32 directed regen ==="
"$PY" tests/gen_vectors_f32.py directed "$R/vecs" > "$R/gen-f32.log" 2>&1
echo "gen_f32 exit=$?"
cat "$R/gen-f32.log"
echo "--- vec file list ---"
ls "$R/vecs"
} > "$R/regen.log" 2>&1
echo "=== per-file diff vs committed ==="
for f in "$R"/vecs/*.vec; do
  b=$(basename "$f")
  if [ -f "tests/vectors/$b" ]; then
    n=$(cmp -s "$f" "tests/vectors/$b" && echo SAME || echo DIFFER)
    echo "$b: $n (regen $(wc -l < "$f") lines vs committed $(wc -l < "tests/vectors/$b") lines)"
  else
    echo "$b: NEW-FILE (not in tests/vectors, $(wc -l < "$f") lines)"
  fi
done
echo done-probe1b
