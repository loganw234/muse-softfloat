#!/usr/bin/env bash
# Render gitvisual7.mp4 with the new popup copy (wave6-popups worktree).
set -u
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w6-popups/video/segments
export MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
"$MSF_PYTHON" gitvisual.py --out gitvisual7.mp4
