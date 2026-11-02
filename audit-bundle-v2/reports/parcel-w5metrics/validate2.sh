#!/usr/bin/env bash
# Final gates on the actual worktree: kit tables + repo smoke budget.
WS=/c/Users/logan/source/repos/Muse-Softfloat
PY=$WS/.venv/Scripts/python.exe
KIT=$WS/softfloat-bootstrap-kit/tools/round_metrics.py
echo "=== round_metrics on worktree docs/metrics ==="
"$PY" "$KIT" "$WS/worktrees/w5-metrics/docs/metrics" --repo "$WS/muse-softfloat" \
  --out "$WS/scratch/parcel-w5metrics/tables-final-all.md"; echo "all exit=$?"
for w in wave4 wave5; do
  "$PY" "$KIT" "$WS/worktrees/w5-metrics/docs/metrics" --wave "$w" --repo "$WS/muse-softfloat" \
    --out "$WS/scratch/parcel-w5metrics/tables-final-$w.md"; echo "$w exit=$?"
done
echo "=== tools/run.sh smoke (worktree) ==="
cd "$WS/worktrees/w5-metrics" || exit 1
bash tools/run.sh smoke > "$WS/scratch/parcel-w5metrics/smoke.log" 2>&1
echo "smoke exit=$?"
tail -5 "$WS/scratch/parcel-w5metrics/smoke.log"
