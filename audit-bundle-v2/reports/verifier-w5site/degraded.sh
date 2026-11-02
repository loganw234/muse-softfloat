#!/bin/bash
# degraded.sh - serve a scratch site copy with WASM blocked, dump via headless Edge.
set -u
cd /c/Users/logan/source/repos/Muse-Softfloat
D=scratch/verifier-w5site/degraded
rm -rf "$D"
cp -r worktrees/verify5-site/site "$D"
mv "$D/msf.wasm" "$D/msf.wasm.blocked"
export TMPDIR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w5site/tmp
export TMP="$TMPDIR" TEMP="$TMPDIR"
mkdir -p "$TMPDIR"
python -m http.server 8931 --directory "$D" >/dev/null 2>&1 &
SRV=$!
sleep 2
EDGE='/c/Program Files (x86)/Microsoft/Edge/Application/156.0.4314.50/msedge.exe'
"$EDGE" --headless --disable-gpu --no-sandbox --virtual-time-budget=8000 --dump-dom http://127.0.0.1:8931/ > "$D/dom.html" 2>"$D/edge-err.txt"
echo EDGE_RC=$?
kill $SRV 2>/dev/null
grep -o 'WebAssembly[^<]*' "$D/dom.html" | head -5
grep -o 'id="wasm-status"[^>]*>[^<]*' "$D/dom.html" | head -3
grep -c 'recorded' "$D/dom.html"
