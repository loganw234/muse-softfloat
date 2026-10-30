#!/usr/bin/env bash
set -u
cd "$(dirname "$0")/../../muse-softfloat" || exit 9
export PATH="/c/Program Files/Git/cmd:/c/Program Files/Git/mingw64/bin:/c/Program Files/Git/usr/bin:/usr/bin:$PATH"
export MSF_PYTHON="$PWD/../.venv/Scripts/python.exe"
export TMPDIR="$PWD/../scratch/lead/tmp" TMP="$PWD/../scratch/lead/tmp" TEMP="$PWD/../scratch/lead/tmp"
mkdir -p "$TMPDIR"
bash tools/run.sh standard
