#!/usr/bin/env bash
# Regenerate explog tables twice; byte-stability + header cmp.
set -eu
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
cd "$ROOT/worktrees/w5-log2"
export MSF_PYTHON="$ROOT/.venv/Scripts/python.exe"
export TMPDIR="$ROOT/scratch/parcel-w5log2/tmp"
mkdir -p "$TMPDIR" build/explog
ulimit -v 2097152 2>/dev/null || true
echo "ulimit -v: $(ulimit -v) (KB, requested 2097152)"
"$MSF_PYTHON" tools/gen_explog_tables.py build/explog/regen1.h
"$MSF_PYTHON" tools/gen_explog_tables.py build/explog/regen2.h
cmp build/explog/regen1.h build/explog/regen2.h && echo "REGEN TWICE BYTE-IDENTICAL"
cp build/explog/regen1.h src/msf_explog_tables.h
cmp build/explog/regen1.h src/msf_explog_tables.h && echo "HEADER MATCHES GENERATOR"
grep -n "EK_EXP\|EK_LOG\|EK_TINY\|NTERMS" src/msf_explog_tables.h | head -8
