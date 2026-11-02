#!/usr/bin/env bash
set -eu
cd "$(dirname "$0")/../.." || exit 9
export MSF_PYTHON="$PWD/.venv/Scripts/python.exe"
export PYTHONUTF8=1
export PYTHONIOENCODING=utf-8
"$MSF_PYTHON" -m py_compile worktrees/w6-captions/video/captions.py
"$MSF_PYTHON" worktrees/w6-captions/video/captions.py --validate --stills
