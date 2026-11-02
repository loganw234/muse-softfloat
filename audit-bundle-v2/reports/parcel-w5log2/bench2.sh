#!/usr/bin/env bash
# pricing bench: 1/16 heavy shard (2^20 patterns, log pair)
set -u
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
cd "$ROOT/worktrees/w5-log2"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export TMPDIR="$ROOT/scratch/parcel-w5log2/tmp"
ulimit -v 4194304 2>/dev/null || true
EXE=build/explog/explog_exhaustive.exe
date '+bench2 start %Y-%m-%d %H:%M:%S %z'
time "$EXE" f32 3f000000 3f100000 4 > "$ROOT/scratch/parcel-w5log2/bench2.log" 2>&1
echo "rc=$?"
cat "$ROOT/scratch/parcel-w5log2/bench2.log"
date '+bench2 end %Y-%m-%d %H:%M:%S %z'
# one negative-domain slice for the fast-shard price
time "$EXE" f32 bf000000 bf100000 4 > "$ROOT/scratch/parcel-w5log2/bench2n.log" 2>&1
echo "rc-neg=$?"
cat "$ROOT/scratch/parcel-w5log2/bench2n.log"
