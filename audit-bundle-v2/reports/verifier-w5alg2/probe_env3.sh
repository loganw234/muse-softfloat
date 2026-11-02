#!/usr/bin/env bash
set -u
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export MSF_PYTHON="${MSF_PYTHON:-$(pwd)/.venv/Scripts/python.exe}"
export PROBE_FOO="hello123"
echo "PARENT MSF_PYTHON=$MSF_PYTHON PROBE_FOO=$PROBE_FOO"
bash -c 'echo CHILD MSF_PYTHON=$MSF_PYTHON PROBE_FOO=$PROBE_FOO'
/c/msys64/usr/bin/bash -c 'echo MSYS2CHILD MSF_PYTHON=$MSF_PYTHON PROBE_FOO=$PROBE_FOO'
env | grep -i -E "msf|probe_foo" || echo "env-grep-empty"
