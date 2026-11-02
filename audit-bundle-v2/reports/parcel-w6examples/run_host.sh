#!/usr/bin/env bash
set -u
export MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w6-examples || exit 9
bash examples/host/build.sh
