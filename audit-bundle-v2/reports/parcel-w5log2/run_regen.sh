#!/usr/bin/env bash
# registration regen: gen_tables in place, twice byte-stable
set -eu
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
cd "$ROOT/worktrees/w5-log2"
export MSF_PYTHON="$ROOT/.venv/Scripts/python.exe"
export TMPDIR="$ROOT/scratch/parcel-w5log2/tmp"
mkdir -p "$TMPDIR"
ulimit -v 2097152 2>/dev/null || true
"$MSF_PYTHON" tools/gen_tables.py
"$MSF_PYTHON" tools/gen_tables.py build/explog/gen-check
for f in include/muse_softfloat.h src/msf_formats.h tests/msf_dispatch.h docs/COVERAGE.tsv; do
    cmp "$f" "build/explog/gen-check/$f" && echo "stable: $f"
done
git status --porcelain | head -20
grep -c "msf16_log2\|msf32_log2\|msf64_log2" tests/msf_dispatch.h || true
