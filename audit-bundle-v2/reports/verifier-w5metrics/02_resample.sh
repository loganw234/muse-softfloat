#!/usr/bin/env bash
# Probe 2b wrapper: resample check with pinned python, ceilings, streamed log.
set -euo pipefail
ulimit -v 4194304 2>/dev/null || true
MSF_PYTHON="${MSF_PYTHON:-C:/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe}"
cd "C:/Users/logan/source/repos/Muse-Softfloat"
"$MSF_PYTHON" scratch/verifier-w5metrics/02_resample.py 2>&1 | tee scratch/verifier-w5metrics/02_resample.log
