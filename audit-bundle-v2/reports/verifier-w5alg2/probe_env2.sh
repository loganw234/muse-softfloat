#!/usr/bin/env bash
# probe_env2.sh - replicate run.sh resolution exactly.
set -u
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export MSF_PYTHON="${MSF_PYTHON:-$(pwd)/.venv/Scripts/python.exe}"
echo "PROBE s11-side MSF_PYTHON=$MSF_PYTHON"
(cd worktrees/verify5-alg2 && bash -c 'echo COPY-SIDE MSF_PYTHON=$MSF_PYTHON; PY="${MSF_PYTHON:-}"; echo COPY-SIDE PY=$PY')
