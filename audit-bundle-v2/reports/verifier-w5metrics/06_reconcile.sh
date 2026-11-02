#!/usr/bin/env bash
# Probe 6 wrapper: streamed recount with pinned python and ceilings.
set -euo pipefail
ulimit -v 4194304 2>/dev/null || true
ulimit -n 4096 2>/dev/null || true
MSF_PYTHON="${MSF_PYTHON:-C:/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe}"
cd "C:/Users/logan/source/repos/Muse-Softfloat"
"$MSF_PYTHON" scratch/verifier-w5metrics/06_reconcile.py 2>&1 | tee scratch/verifier-w5metrics/06_reconcile.log
