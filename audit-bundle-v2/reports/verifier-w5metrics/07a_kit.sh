#!/usr/bin/env bash
# Probe 7a: kit round_metrics.py selftest + tables over the copy's files.
set -euo pipefail
ulimit -v 2097152 2>/dev/null || true
MSF_PYTHON="${MSF_PYTHON:-C:/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe}"
cd "C:/Users/logan/source/repos/Muse-Softfloat"
KIT="softfloat-bootstrap-kit/tools/round_metrics.py"
COPY="worktrees/verify5-metrics"
OUT="scratch/verifier-w5metrics/kit-tables"
mkdir -p "$OUT"
echo "--- selftest ---"
"$MSF_PYTHON" "$KIT" --selftest
echo "--- all waves ---"
"$MSF_PYTHON" "$KIT" "$COPY/docs/metrics" --repo "$COPY" --out "$OUT/all.md"
echo "exit=$?"
echo "--- wave4 ---"
"$MSF_PYTHON" "$KIT" "$COPY/docs/metrics" --wave wave4 --repo "$COPY" --out "$OUT/wave4.md"
echo "exit=$?"
echo "--- wave5 ---"
"$MSF_PYTHON" "$KIT" "$COPY/docs/metrics" --wave wave5 --repo "$COPY" --out "$OUT/wave5.md"
echo "exit=$?"
ls -la "$OUT"
