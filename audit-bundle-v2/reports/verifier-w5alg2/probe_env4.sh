#!/usr/bin/env bash
set -u
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export MSF_PYTHON="${MSF_PYTHON:-$(pwd)/.venv/Scripts/python.exe}"
export MSF_ALG_DECIDER="$(pwd)/scratch/verifier-w5alg2/out/alg_decider.exe"
export PROBE_FOO="hello123"
export PATH_EXTRA_TEST="qqq"
echo "PARENT PATH reflected: $(echo $PATH | cut -c1-60)"
$MSF_PYTHON -c "import os; print('PY-CHILD MSF_PYTHON=', repr(os.environ.get('MSF_PYTHON'))); print('PY-CHILD MSF_ALG_DECIDER=', repr(os.environ.get('MSF_ALG_DECIDER'))); print('PY-CHILD PROBE_FOO=', repr(os.environ.get('PROBE_FOO')))"
ls worktrees/verify5-alg2/build/alg/alg_decider.exe 2>&1 || echo "no stale decider in copy"
