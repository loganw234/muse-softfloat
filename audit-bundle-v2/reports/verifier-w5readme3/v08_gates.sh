#!/usr/bin/env bash
# v08_gates.sh - drift check + unit tests, all outputs to scratch.
set -u
ROOT="$PWD"
V="$ROOT/worktrees/verify5-readme3"
B="$ROOT/scratch/verifier-w5readme3/build"
export PATH=/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH
mkdir -p "$B/tmp" "$B/gen-check"
export TMPDIR="$B/tmp" TMP="$B/tmp" TEMP="$B/tmp"
export MSF_PYTHON="$ROOT/.venv/Scripts/python.exe"
cd "$V"
"$MSF_PYTHON" tools/gen_tables.py "$B/gen-check" > "$B/gen.log" 2>&1 || { echo "GEN FAIL"; tail -5 "$B/gen.log"; exit 1; }
for f in include/muse_softfloat.h src/msf_formats.h tests/msf_dispatch.h docs/COVERAGE.tsv; do
  if cmp -s "$f" "$B/gen-check/$f"; then echo "drift-ok: $f"; else echo "DRIFT: $f"; fi
done
"$B/msf_runner.exe" unit > "$B/unit.log" 2>&1
echo "unit exit: $?"
grep -E 'unit |VERDICT|PASS|FAIL' "$B/unit.log" | tail -8
