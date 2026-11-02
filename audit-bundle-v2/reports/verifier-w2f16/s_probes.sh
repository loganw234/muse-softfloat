#!/usr/bin/env bash
# s_probes.sh - claim surface, directed replay, regen, standard
set -u
CP="C:/Users/logan/source/repos/Muse-Softfloat/worktrees/verify2-f16"
SC="C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w2f16"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export MSF_HOST_CC=gcc
export MSF_PYTHON="C:/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe"
cd "$CP" || exit 9
{
echo "=== implemented.tsv append check ==="
git diff dd48b08 -- tables/implemented.tsv | head -5
git show dd48b08:tables/implemented.tsv | wc -l
wc -l tables/implemented.tsv
echo "=== non-append changes in implemented.tsv (should be empty) ==="
git diff dd48b08 -- tables/implemented.tsv | grep -E '^[-]' | grep -v '^---' | head -20
echo "=== COVERAGE/header/dispatch diff sanity (regenerated outputs) ==="
git diff dd48b08 --stat -- docs/COVERAGE.tsv include/muse_softfloat.h tests/msf_dispatch.h
echo "=== src/msf16.c brief-ownership check ==="
git diff dd48b08 --stat -- src/
echo "=== regenerated-output drift (gen_tables to temp, byte-compare) ==="
"$MSF_PYTHON" tools/gen_tables.py "$SC/gen-check" > "$SC/gen-tables.log" 2>&1
for f in include/muse_softfloat.h tests/msf_dispatch.h docs/COVERAGE.tsv; do
  if cmp -s "$f" "$SC/gen-check/$f"; then echo "IDENTICAL: $f"; else echo "DRIFT: $f"; fi
done
echo "=== implemented.tsv vs regeneration ==="
if cmp -s tables/implemented.tsv "$SC/gen-check/tables/implemented.tsv"; then echo "IDENTICAL: tables/implemented.tsv"; else echo "DIFF-IMPLEMENTED (expected: appends of 236 rows)"; diff <(git show dd48b08:tables/implemented.tsv) tables/implemented.tsv | head -5; wc -l tables/implemented.tsv "$SC/gen-check/tables/implemented.tsv"; fi
} > "$SC/probe2-drift.log" 2>&1
echo "probe2 done"
{
echo "=== directed replay of committed f16 vectors ==="
R="build/smoke/msf_runner.exe"
for v in tests/vectors/arith-f16.vec tests/vectors/compare-f16.vec tests/vectors/conv-int-f16.vec tests/vectors/fma-sqrt-f16.vec tests/vectors/rint-misc-f16.vec tests/vectors/toint-f16.vec; do
  "$R" verify "$v" > "$SC/replay-$(basename "$v" .vec).log" 2>&1
  echo "$v exit=$? : $(grep -E '^(total|VERDICT)' "$SC/replay-$(basename "$v" .vec).log")"
done
} > "$SC/probe3-replay.log" 2>&1
echo "probe3 replay done"
{
echo "=== regenerate directed files from generator to temp, byte-compare ==="
mkdir -p "$SC/regen"
"$MSF_PYTHON" tests/gen_vectors_f16.py --out-dir "$SC/regen" > "$SC/regen-gen.log" 2>&1
echo "gen exit=$?"
ls "$SC/regen" >> "$SC/regen-gen.log" 2>&1
for f in "$SC"/regen/*.vec; do
  b=$(basename "$f")
  if cmp -s "$f" "tests/vectors/$b"; then echo "IDENTICAL: $b"; else echo "DIFF: $b"; fi
done
} > "$SC/probe3-regen.log" 2>&1
echo "probe3 regen done"
