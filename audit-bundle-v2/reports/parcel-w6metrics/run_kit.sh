#!/usr/bin/env bash
# Kit validation on the scratch combined copies (only the 4 owned files present;
# absent plants/corrections tables are omitted by the tool and say so).
WS=/c/Users/logan/source/repos/Muse-Softfloat
PY=$WS/.venv/Scripts/python.exe
KIT=$WS/softfloat-bootstrap-kit/tools/round_metrics.py
DIR=$WS/scratch/parcel-w6metrics/combined-check
REPO=$WS/worktrees/w6-metrics
echo "=== kit selftest ==="
"$PY" "$KIT" --selftest || exit 1
for w in all wave5 polish wave6; do
  if [ "$w" = all ]; then
    "$PY" "$KIT" "$DIR" --repo "$REPO" --out "$WS/scratch/parcel-w6metrics/tables-$w.md" || exit 1
  else
    "$PY" "$KIT" "$DIR" --wave "$w" --repo "$REPO" --out "$WS/scratch/parcel-w6metrics/tables-$w.md" || exit 1
  fi
  echo "tables $w: exit 0"
done
