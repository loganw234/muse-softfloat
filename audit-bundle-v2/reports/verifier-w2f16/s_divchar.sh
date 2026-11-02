#!/usr/bin/env bash
# s_divchar.sh - split div failures into value vs flag-only mismatches
set -u
cd "C:/Users/logan/source/repos/Muse-Softfloat/worktrees/verify2-f16" || exit 9
C:/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe \
  C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w2f16/divchar.py
