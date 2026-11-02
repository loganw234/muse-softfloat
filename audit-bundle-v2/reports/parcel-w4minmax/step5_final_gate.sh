#!/usr/bin/env bash
set -u
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w4-minmax || exit 9
export MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
S=/c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w4minmax
PY=$MSF_PYTHON
echo "== regeneration byte-identical: tables =="
rm -rf build/gate-t2/regen-check build/gate-t2/regen-vecs
$PY tools/gen_tables.py build/gate-t2/regen-check > "$S/regen-tables.log" 2>&1 || exit 1
cat "$S/regen-tables.log"
for f in include/muse_softfloat.h src/msf_formats.h tests/msf_dispatch.h docs/COVERAGE.tsv; do
  cmp -s "$f" "build/gate-t2/regen-check/$f" && echo "identical: $f" || { echo "DRIFT: $f"; exit 1; }
done
echo "== regeneration byte-identical: directed vectors =="
$PY tests/gen_vectors_tier2.py directed build/gate-t2/regen-vecs > "$S/regen-vecs.log" 2>&1 || exit 1
cat "$S/regen-vecs.log"
for f in minmax-f16.vec minmax-f32.vec minmax-f64.vec payload-f16.vec payload-f32.vec payload-f64.vec; do
  cmp -s "tests/vectors/$f" "build/gate-t2/regen-vecs/$f" && echo "identical: tests/vectors/$f" || { echo "DRIFT: $f"; exit 1; }
done
echo "== standard budget =="
bash tools/run.sh standard > "$S/standard1.log" 2>&1
rc=$?
echo "standard rc=$rc"
tail -8 "$S/standard1.log"
grep -E '^inventory:' "$S/standard1.log" || true
grep -E '^budget ' "$S/standard1.log" || true
[ $rc -eq 0 ] || exit 1
echo "== explicit t2 replay with standard runner =="
T2="tests/vectors/minmax-f16.vec tests/vectors/minmax-f32.vec tests/vectors/minmax-f64.vec tests/vectors/payload-f16.vec tests/vectors/payload-f32.vec tests/vectors/payload-f64.vec build/gate-t2/payload-f16-exhaustive.vec build/gate-t2/seeded-f32f64.vec build/gate-t2/minmax-f16-sweep.vec"
awk '!/^#/ && NF>0 {print $NF}' $T2 | sort | uniq -c | awk '{print $2, $1}' > build/gate-t2/expect-all-t2.txt
cat build/gate-t2/expect-all-t2.txt
build/standard/msf_runner.exe verify --expect-counts build/gate-t2/expect-all-t2.txt $T2 > "$S/replay-all-t2.log" 2>&1
rc=$?
echo "all-t2 replay rc=$rc"
grep -E '^(file|prov|total|VERDICT)' "$S/replay-all-t2.log"
[ $rc -eq 0 ] || exit 1
echo "== hand-written lines =="
wc -l src/msf_performat.inc tests/gen_vectors_tier2.py
git -c safe.directory=/c/Users/logan/source/repos/Muse-Softfloat/worktrees/w4-minmax diff --numstat
echo FINAL-GATE-PASS
