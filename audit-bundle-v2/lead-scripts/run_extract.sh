#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 9
mkdir -p scratch/lead/tmp
export TMPDIR=$PWD/scratch/lead/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\lead\tmp'
export TEMP="$TMP"
PY="$PWD/.venv/Scripts/python.exe"
SESS='/c/Users/logan/.local/share/muse/sessions/2026/10/26/01a17907-4147-7333-a565-56071da9d971'
cd muse-softfloat || exit 9
echo "=== selftest ==="
"$PY" tools/extract_session_metrics.py --selftest
echo "selftest rc=$?"
echo "=== extract this session ==="
"$PY" tools/extract_session_metrics.py --session-dir "$SESS" --wave wave0 --out-dir docs/metrics \
  --until '2026-10-26T11:31:34-07:00' \
  --author-commit lead=dfc7a0200993470adf8d52b7d4d6da4d830bded0 \
  --verdict 'verifier-phase0=0,3,NOT READY,true' \
  --verdict 'rechecker-phase0=0,1,NOT READY,true' \
  --verdict 'rechecker2-phase0=0,0,READY,false' \
  --verdict 'verifier-wave0=0,2,NOT READY,true'
echo "extract rc=$?"
echo "=== round_metrics on the JSONL ==="
GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=safe.directory GIT_CONFIG_VALUE_0='C:/Users/logan/source/repos/Muse-Softfloat/muse-softfloat' \
  "$PY" -I ../softfloat-bootstrap-kit/tools/round_metrics.py docs/metrics --repo . --out ../scratch/lead/wave0-tables.md
echo "round_metrics rc=$?"
head -60 ../scratch/lead/wave0-tables.md 2>/dev/null
