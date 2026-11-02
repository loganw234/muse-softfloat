#!/usr/bin/env bash
set -u
cd "$(dirname "$0")/../.." || exit 9
export MSF_PYTHON="$PWD/.venv/Scripts/python.exe"
export PYTHONUTF8=1
export PYTHONIOENCODING=utf-8
"$MSF_PYTHON" scratch/parcel-w6captions/dump_audit.py
