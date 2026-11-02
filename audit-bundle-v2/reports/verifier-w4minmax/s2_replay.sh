#!/usr/bin/env bash
# verifier-w4minmax s2: explicit replay of all six committed Tier 2
# vector files with expect-counts derived from the files.
set -u
COPY=/c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify4-minmax
SCR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w4minmax
export MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
OUT=$SCR/out-replay
mkdir -p "$OUT"
cd "$COPY" || exit 9
R=build/smoke/msf_runner.exe
[ -x "$R" ] || { echo "runner missing: $R"; exit 9; }
echo "== files =="
wc -l tests/vectors/minmax-f16.vec tests/vectors/minmax-f32.vec tests/vectors/minmax-f64.vec tests/vectors/payload-f16.vec tests/vectors/payload-f32.vec tests/vectors/payload-f64.vec
echo "== provenance tags in Tier 2 files =="
awk '!/^#/ && NF>0 {print $NF}' tests/vectors/minmax-f16.vec tests/vectors/minmax-f32.vec tests/vectors/minmax-f64.vec tests/vectors/payload-f16.vec tests/vectors/payload-f32.vec tests/vectors/payload-f64.vec | sort | uniq -c
echo "== names present per file =="
for f in tests/vectors/minmax-f16.vec tests/vectors/minmax-f32.vec tests/vectors/minmax-f64.vec; do echo "-- $f"; awk '!/^#/ && NF>0 {print $1}' "$f" | sort | uniq -c; done
for f in tests/vectors/payload-f16.vec tests/vectors/payload-f32.vec tests/vectors/payload-f64.vec; do echo "-- $f"; awk '!/^#/ && NF>0 {print $1}' "$f" | sort | uniq -c; done
awk '!/^#/ && NF>0 {print $NF}' tests/vectors/minmax-f16.vec tests/vectors/minmax-f32.vec tests/vectors/minmax-f64.vec tests/vectors/payload-f16.vec tests/vectors/payload-f32.vec tests/vectors/payload-f64.vec | sort | uniq -c | awk '{print $2, $1}' > "$OUT/expect-t2.txt"
echo "== expect-t2.txt =="
cat "$OUT/expect-t2.txt"
"$R" verify --expect-counts "$OUT/expect-t2.txt" tests/vectors/minmax-f16.vec tests/vectors/minmax-f32.vec tests/vectors/minmax-f64.vec tests/vectors/payload-f16.vec tests/vectors/payload-f32.vec tests/vectors/payload-f64.vec > "$OUT/replay.log" 2>&1
rc=$?
echo "REPLAY_RC=$rc"
grep -E '^(file|prov|total|VERDICT|COUNT|MANIFEST)' "$OUT/replay.log" | head -30
grep -E '^FAIL' "$OUT/replay.log" | head -20
echo "fail-line-count=$(grep -c '^FAIL' "$OUT/replay.log")"
exit 0
