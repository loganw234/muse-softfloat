#!/usr/bin/env bash
# verifier-w164 debug: probe ref_scaleb outputs.
set -uo pipefail
cd /c/Users/logan/source/repos/Muse-Softfloat
PY=../../.venv/Scripts/python.exe
.venv/Scripts/python.exe scratch/verifier-w1f64/v-dbg.py
