#!/usr/bin/env bash
# Emit one line per new/changed file under ledger/urgent or new parcel
# ledger entry (entry count change), so escalations surface as events.
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 9
declare -A seen
snapshot() {
  for f in ledger/urgent/* ledger/parcel-f64.md ledger/parcel-f32.md; do
    [ -f "$f" ] || continue
    sig=$(stat -c '%s-%Y' "$f" 2>/dev/null)
    if [ "${seen[$f]:-}" != "$sig" ]; then
      seen[$f]="$sig"
      echo "ledger-change: $f ($sig) at $(date '+%H:%M:%S')"
    fi
  done
}
snapshot
while sleep 25; do snapshot; done
