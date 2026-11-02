#!/usr/bin/env bash
# probe_env.sh - diagnose MSF_PYTHON handoff into run.sh.
set -u
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
if [ -z "$MSF_PYTHON" ]; then
  MSF_PYTHON="$(pwd)/.venv/Scripts/python.exe"
fi
export MSF_PYTHON
echo "PROBE s11-side MSF_PYTHON=$MSF_PYTHON"
(cd worktrees/verify5-alg2 && bash -c 'echo PROBE copy-side MSF_PYTHON=$MSF_PYTHON')
