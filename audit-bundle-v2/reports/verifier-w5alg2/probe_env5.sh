#!/usr/bin/env bash
set -u
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export MSF_PYTHON="${MSF_PYTHON:-$(pwd)/.venv/Scripts/python.exe}"
export PROBE_FOO="hello123"
echo "--- export -p ---"
export -p | grep -i -E "msf|probe" || echo "export-p-empty"
echo "--- env ---"
env | grep -i -E "msf|probe" || echo "env-empty"
echo "--- declare -p ---"
declare -p MSF_PYTHON PROBE_FOO || echo "declare-failed"
echo "--- bash child env ---"
bash -c 'export -p' | grep -i -E "msf|probe" || echo "child-export-p-empty"
