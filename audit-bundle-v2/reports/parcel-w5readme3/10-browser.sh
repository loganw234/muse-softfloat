#!/usr/bin/env bash
# 10-browser.sh - headless Edge DOM proof over a local static serve.
# Skip-by-name if Edge is absent; the Node replay remains the gate.
set -u
WS=/c/Users/logan/source/repos/Muse-Softfloat
cd "$WS" || exit 9
ulimit -t 600 2>/dev/null || true
export MSF_PYTHON=$WS/.venv/Scripts/python.exe
export TMPDIR=$WS/scratch/parcel-w5readme3/tmp
export TMP="$(cygpath -w "$TMPDIR" 2>/dev/null || echo "$TMPDIR")"
export TEMP="$TMP"
WT=$WS/worktrees/w5-readme3
OUT=$WS/scratch/parcel-w5readme3/out
PORT=18765
EDGE=""
for c in "/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" \
         "/c/Program Files/Microsoft/Edge/Application/msedge.exe"; do
  if [ -f "$c" ]; then EDGE="$c"; break; fi
done
if [ -z "$EDGE" ]; then echo "EDGE: SKIP-BY-NAME msedge.exe not found at standard paths"; exit 0; fi
echo "edge: $EDGE"
"$MSF_PYTHON" -m http.server $PORT --directory "$WT/site" --bind 127.0.0.1 > "$OUT/http.log" 2>&1 &
SRV=$!
trap 'kill $SRV 2>/dev/null; wait $SRV 2>/dev/null' EXIT
sleep 2
if ! kill -0 $SRV 2>/dev/null; then echo "http server failed to start:"; cat "$OUT/http.log"; exit 1; fi
echo "http server pid: $SRV (killed on exit)"
curl -s "http://127.0.0.1:$PORT/data.json" | head -c 220; echo
mkdir -p scratch/parcel-w5readme3/edge-profile
"$EDGE" --headless=new --disable-gpu --no-first-run \
  --user-data-dir="$WS/scratch/parcel-w5readme3/edge-profile" \
  --virtual-time-budget=15000 --dump-dom "http://127.0.0.1:$PORT/" > "$OUT/dom.html" 2> "$OUT/edge.log"
rc=$?
echo "edge exit: $rc (dom bytes: $(wc -c < "$OUT/dom.html"))"
for s in "WebAssembly build ready" "849" "411" "109 of 115" "head+tail" "SF-2 close" "0x40000000" "822 of 849"; do
  if grep -qF "$s" "$OUT/dom.html"; then echo "dom has: $s"; else echo "dom MISSING: $s"; rc=1; fi
done
grep -o 'Status at [^<]*' "$OUT/dom.html" | head -2 || true
exit $rc
