#!/usr/bin/env bash
# static probes: drift check, type scan, non-str regression via probe runner.
R=/c/Users/logan/source/repos/Muse-Softfloat
export TMPDIR=$R/scratch/verifier-w3str/tmp
export TMP="C:\Users\logan\source\repos\Muse-Softfloat\scratch\verifier-w3str\tmp"
export TEMP="$TMP"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
cd "$R/worktrees/verify3-str" || exit 9
PY="$R/.venv/Scripts/python.exe"
echo "=== drift check (gen_tables vs committed):"
rm -rf "$R/scratch/verifier-w3str/gen-check"
"$PY" tools/gen_tables.py "$R/scratch/verifier-w3str/gen-check" > "$R/scratch/verifier-w3str/gen.log" 2>&1
echo "gen exit=$?"
for f in include/muse_softfloat.h src/msf_formats.h tests/msf_dispatch.h docs/COVERAGE.tsv; do
  if cmp -s "$f" "$R/scratch/verifier-w3str/gen-check/$f"; then echo "$f IDENTICAL"; else echo "$f DIFFERS"; fi
done
echo "=== type scan:"
if grep -rnwE 'float|double' src include > "$R/scratch/verifier-w3str/typescan.txt" 2>&1; then
  echo "TYPE HITS:"; cat "$R/scratch/verifier-w3str/typescan.txt"
else
  echo "type scan: clean"
fi
echo "=== non-str regression (29 wired VECS via probe runner):"
VECS="tests/vectors/encodings-f16.vec tests/vectors/encodings-f32.vec tests/vectors/encodings-f64.vec tests/vectors/copysign.vec tests/vectors/pack64.vec tests/vectors/pack32.vec tests/vectors/pack16.vec tests/vectors/arith-f32.vec tests/vectors/fma-sqrt-f32.vec tests/vectors/conv-int-f32.vec tests/vectors/toint-f32.vec tests/vectors/rint-misc-f32.vec tests/vectors/compare-f32.vec tests/vectors/arith-f64.vec tests/vectors/conv-f64.vec tests/vectors/misc-f64.vec tests/vectors/compare-f64.vec tests/vectors/nan-f64.vec tests/vectors/arith-f16.vec tests/vectors/fma-sqrt-f16.vec tests/vectors/conv-int-f16.vec tests/vectors/toint-f16.vec tests/vectors/rint-misc-f16.vec tests/vectors/compare-f16.vec tests/vectors/arith-xf.vec tests/vectors/fma-sqrt-xf.vec tests/vectors/conv-xf.vec tests/vectors/compare-xf.vec tests/vectors/traps-xf.vec"
"$R/scratch/verifier-w3str/runner.exe" verify $VECS > "$R/scratch/verifier-w3str/regress-nonstr.log" 2>&1
echo "verify exit=$?"
grep -E '^(total|VERDICT)' "$R/scratch/verifier-w3str/regress-nonstr.log"
