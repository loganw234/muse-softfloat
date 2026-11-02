#!/usr/bin/env bash
# parcel-w6judgemap probe 3: standard (merge gate) + sanitize trap + audit manifest verify
set -u
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w6-judgemap || exit 9
export MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
LOG=/c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w6judgemap
"$MSF_PYTHON" -c "import json,collections; ops=json.load(open('site/ops.json')); print('ops runnable', sum(o['runnable'] for o in ops), 'pair', sum(o['pair'] for o in ops), 'nonrunnable', sum(not o['runnable'] for o in ops))"
bash tools/run.sh standard > "$LOG/standard-before.log" 2>&1; echo "standard rc=$?"
grep -E "VERDICT|budget standard|extras|pack64|aug|exhaustive|checks" "$LOG/standard-before.log" | tail -40
bash tools/run.sh sanitize > "$LOG/sanitize-trap.log" 2>&1; echo "sanitize rc=$?"
grep -E "VERDICT|budget sanitize|canar|SKIP|findings|PASS|FAIL" "$LOG/sanitize-trap.log" | tail -30
cd audit-bundle || exit 9
sha256sum -c MANIFEST.sha256 > "$LOG/audit-manifest.log" 2>&1; echo "manifest rc=$?"
grep -c ": OK" "$LOG/audit-manifest.log"; grep -v ": OK" "$LOG/audit-manifest.log" | head -10
