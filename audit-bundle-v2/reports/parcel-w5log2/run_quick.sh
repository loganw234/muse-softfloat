#!/usr/bin/env bash
# spot probes + f16 exhaustive (all 4 functions)
set -u
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
cd "$ROOT/worktrees/w5-log2"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export TMPDIR="$ROOT/scratch/parcel-w5log2/tmp"
mkdir -p "$TMPDIR"
ulimit -v 4194304 2>/dev/null || true
EXE=build/explog/explog_exhaustive.exe
echo "== log2(2)=1 f64 in 4000000000000000 fn2 =="
"$EXE" one 2 2 4000000000000000
echo "== log2(1)=+0 in 3ff0000000000000 =="
"$EXE" one 2 2 3ff0000000000000
echo "== log2(+0) pole in 0 =="
"$EXE" one 2 2 0
echo "== log2(-0) pole in 8000000000000000 =="
"$EXE" one 2 2 8000000000000000
echo "== log2p1(-1) pole in bff0000000000000 fn3 =="
"$EXE" one 2 3 bff0000000000000
echo "== log2p1(2^1022) sticky attractor in 7fe0000000000000 =="
"$EXE" one 2 3 7fe0000000000000
echo "== log2 hardest in 7fe61555f75885b4 =="
"$EXE" one 2 2 7fe61555f75885b4
echo "== log2p1 hardest in 44ee499f19ecc9fb =="
"$EXE" one 2 3 44ee499f19ecc9fb
echo "== log2p1 tiny subnormal in 1 =="
"$EXE" one 2 3 1
echo "== log2p1 tiny neg subnormal in 8000000000000001 =="
"$EXE" one 2 3 8000000000000001
echo "== f16 exhaustive all4 =="
time "$EXE" f16
echo "f16 rc=$?"
