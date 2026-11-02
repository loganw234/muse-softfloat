#!/usr/bin/env bash
# 07-verify-site.sh - determinism + surface probes + syntax checks.
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
OUT=$PWD/scratch/parcel-w5readme3/out
WT=$PWD/worktrees/w5-readme3
cd "$WT" || exit 9
echo "date: $(date '+%Y-%m-%d %H:%M:%S %z')"
echo "--- rebuild determinism (second full build) ---"
sha256sum site/msf.wasm > "$OUT/wasm-sha-1.txt"
"$MSF_PYTHON" site/build.py --cc "zig cc" > "$OUT/site-build-2.log" 2>&1
rc=$?
echo "second build exit: $rc"
tail -4 "$OUT/site-build-2.log"
sha256sum site/msf.wasm > "$OUT/wasm-sha-2.txt"
cat "$OUT/wasm-sha-1.txt" "$OUT/wasm-sha-2.txt"
if cmp -s "$OUT/wasm-sha-1.txt" "$OUT/wasm-sha-2.txt"; then echo "wasm: byte-identical across builds"; else echo "wasm: DIFFERS across builds"; rc=1; fi
echo "--- surface probes ---"
node "$PWD/scratch/parcel-w5readme3/probe_wasm.mjs" "$WT/site" > "$OUT/probe-wasm.log" 2>&1
prc=$?
cat "$OUT/probe-wasm.log"
[ $prc -ne 0 ] && rc=1
echo "--- syntax / parse checks ---"
node --check site/app.js && echo "app.js: node --check ok"
"$MSF_PYTHON" -m py_compile site/build_data.py site/build.py && echo "build scripts: py_compile ok"
"$MSF_PYTHON" -c "import json; [json.load(open('site/'+f, encoding='utf-8')) for f in ('data.json','ops.json','vectors-sample.json')]; print('json: all parse')"
echo "--- data.json sample block ---"
"$MSF_PYTHON" -c "import json; d=json.load(open('site/data.json', encoding='utf-8')); print(json.dumps(d['sample'], indent=1)); print('base:', d['base']); print('plants:', d['plants']['caught'], '/', d['plants']['total'], d['plants']['by_wave'])"
echo "--- diff stat (site) ---"
git -c "safe.directory=$WT" -C "$WT" diff --stat
exit $rc
