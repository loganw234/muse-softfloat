#!/bin/bash
# Probe 3d/5/6: RECORD wave sections, coverage enumeration, gate run.
set -u
DUP="C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w6metrics/dup"
OUT="C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w6metrics/out"
export MSF_PYTHON="C:/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe"
cd "$DUP"
echo "=== Sums-for lines in RECORD.md ==="
grep -n 'Sums for' docs/RECORD.md | head -30
echo "=== wave section headers ==="
grep -n '^#' docs/RECORD.md | head -40
