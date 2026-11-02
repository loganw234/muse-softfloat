#!/usr/bin/env bash
# Probe 2a: sanctioned extractor selftest, run from the copy (never modified).
set -euo pipefail
ulimit -v 2097152 2>/dev/null || true
MSF_PYTHON="${MSF_PYTHON:-C:/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe}"
COPY="C:/Users/logan/source/repos/Muse-Softfloat/worktrees/verify5-metrics"
"$MSF_PYTHON" "$COPY/tools/extract_session_metrics.py" --selftest
