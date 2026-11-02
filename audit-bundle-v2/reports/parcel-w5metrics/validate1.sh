#!/usr/bin/env bash
# Validate combined (frozen+new) metrics with the kit's round_metrics.py.
WS=/c/Users/logan/source/repos/Muse-Softfloat
PY=$WS/.venv/Scripts/python.exe
KIT=$WS/softfloat-bootstrap-kit/tools/round_metrics.py
SRC=$WS/worktrees/w5-metrics/docs/metrics
NEW=$WS/scratch/parcel-w5metrics
CHK=$NEW/combined-check
rm -rf "$CHK"; mkdir -p "$CHK"
for f in usage passes escalations briefs; do
  cat "$SRC/$f.jsonl" "$NEW/new-$f.jsonl" > "$CHK/$f.jsonl"
done
cp "$SRC/plants.jsonl" "$SRC/corrections.jsonl" "$CHK/"
wc -l "$CHK"/*.jsonl
echo "=== round_metrics selftest ==="
"$PY" "$KIT" --selftest | tail -2
echo "=== all waves ==="
"$PY" "$KIT" "$CHK" --repo "$WS/muse-softfloat" --out "$NEW/tables-all.md"; echo "exit=$?"
for w in wave0 wave1 wave2 wave3 wave4 wave5; do
  "$PY" "$KIT" "$CHK" --wave "$w" --repo "$WS/muse-softfloat" --out "$NEW/tables-$w.md"
  echo "$w exit=$?"
done
