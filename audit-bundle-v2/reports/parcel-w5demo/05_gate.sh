#!/usr/bin/env bash
set -u
WS=/c/Users/logan/source/repos/Muse-Softfloat
FRESH=$WS/scratch/parcel-w5demo/fresh
rm -rf "$FRESH"
mkdir -p "$FRESH/clone"
cd "$WS/worktrees/w5-demo" || exit 9
TIP=$(git rev-parse HEAD)
echo "archive tip: $TIP ($(git log -1 --oneline))"
git archive HEAD | tar -x -C "$FRESH/clone"
cd "$FRESH/clone" || exit 9
echo "fresh tree: $(pwd)"; ls demo
echo "cache present? $(test -e demo/cache && echo yes || echo no)"

echo "===== GATE 1: --offline with EMPTY cache (must fail pre-network) ====="
bash demo/run_demo.sh host --offline > "$FRESH/gate1-offline-empty.log" 2>&1
echo "GATE1_EXIT=$? (want non-zero)"
grep -E "offline|FAIL|REFUSED" "$FRESH/gate1-offline-empty.log" | head -8

echo "===== GATE 2: host with network, empty cache (must go green) ====="
time bash demo/run_demo.sh host > "$FRESH/gate2-host-online.log" 2>&1
echo "GATE2_EXIT=$? (want 0)"
tail -30 "$FRESH/gate2-host-online.log"

echo "===== GATE 3: board dry refusal (must refuse, no lock, no flash) ====="
ls "$WS/ledger/board.lock" 2>/dev/null && echo "LOCK EXISTS BEFORE (unexpected)" || echo "no workspace board.lock before"
PICO_SDK_PATH=/nonexistent-demo-gate MSF_PICOTOOL=/nonexistent-demo-gate \
  bash demo/run_demo.sh board --offline > "$FRESH/gate3-board-refusal.log" 2>&1
echo "GATE3_EXIT=$? (want 1)"
grep -E "REFUSED|missing|flashed|lock|summary|PASS|FAIL" "$FRESH/gate3-board-refusal.log" | head -20
ls "$WS/ledger/board.lock" 2>/dev/null && echo "LOCK EXISTS AFTER (BAD)" || echo "no workspace board.lock after (good)"
find "$FRESH" -name "board.lock" | head -3
echo "GATE SCRIPT DONE"
