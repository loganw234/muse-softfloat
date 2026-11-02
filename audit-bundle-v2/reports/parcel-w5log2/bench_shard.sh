#!/usr/bin/env bash
# day-1 bench: one heavy shard (positive normals ~0.5..2)
set -u
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
cd "$ROOT/worktrees/w5-log2"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export TMPDIR="$ROOT/scratch/parcel-w5log2/tmp"
ulimit -v 4194304 2>/dev/null || true
EXE=build/explog/explog_exhaustive.exe
date '+bench start %Y-%m-%d %H:%M:%S %z'
time "$EXE" f32 3f000000 40000000 4
date '+bench end %Y-%m-%d %H:%M:%S %z'
