#!/usr/bin/env bash
# 17-gate.sh - run the copy's own smoke gate; record the outcome.
# Must be run with CWD inside the copy (run.sh cds to its own dir).
set -u
export MSF_PYTHON="/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe"
tools/run.sh smoke
