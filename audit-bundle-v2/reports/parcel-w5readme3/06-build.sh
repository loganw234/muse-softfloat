#!/usr/bin/env bash
# 06-build.sh - rebuild site data + msf.wasm + replay (HEAD must be e9c57fb
# so data.json stamps the base commit).
set -u
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 9
ulimit -t 1200 2>/dev/null || true
export MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
export TMPDIR=$PWD/scratch/parcel-w5readme3/tmp
export TMP="$(cygpath -w "$TMPDIR" 2>/dev/null || echo "$TMPDIR")"
export TEMP="$TMP"
export PATH="$PWD/scratch/parcel-w5site/zig-x86_64-windows-0.17.0:$PATH"
export ZIG_GLOBAL_CACHE_DIR="$PWD/scratch/parcel-w5site/zig-cache/global"
export ZIG_LOCAL_CACHE_DIR="$PWD/scratch/parcel-w5site/zig-cache/local"
mkdir -p "$ZIG_GLOBAL_CACHE_DIR" "$ZIG_LOCAL_CACHE_DIR" scratch/parcel-w5readme3/out
OUT=$PWD/scratch/parcel-w5readme3/out
WT=$PWD/worktrees/w5-readme3
echo "date: $(date '+%Y-%m-%d %H:%M:%S %z')"
echo "HEAD: $(git -c "safe.directory=$WT" -C "$WT" rev-parse --short HEAD) (expect e9c57fb)"
echo "zig: $(zig version 2>&1) at $(command -v zig)"
echo "node: $(node --version 2>&1)"
cd "$WT" || exit 9
"$MSF_PYTHON" site/build.py --cc "zig cc" > "$OUT/site-build.log" 2>&1
rc=$?
echo "site build exit: $rc"
cat "$OUT/site-build.log"
echo "--- replay-log.txt ---"
cat site/replay-log.txt
echo "--- data.json (head) ---"
head -30 site/data.json
echo "--- wasm ---"
wc -c site/msf.wasm
sha256sum site/msf.wasm
echo "--- git status ---"
git -c "safe.directory=$WT" -C "$WT" status --short
exit $rc
