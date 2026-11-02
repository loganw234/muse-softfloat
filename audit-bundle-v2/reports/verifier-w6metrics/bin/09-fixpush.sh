#!/bin/bash
# Probe 2e/3c/5: fixer commit identity, RECORD tables, coverage enumeration.
set -u
DUP="C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w6metrics/dup"
OUT="C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w6metrics/out"
export MSF_PYTHON="C:/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe"
cd "$DUP"
echo "=== wave6-popups tip full sha vs passes-row commit ==="
git rev-parse wave6-popups 2>&1
echo "row: ef0215b140a0eeb12ea3d4e64113a4ea0421b053"
git log --format='%H %P %s' -1 wave6-popups 2>&1
git merge-base --is-ancestor ef0215b140a0eeb12ea3d4e64113a4ea0421b053 cdc40ae 2>&1 && echo "fixer-commit ancestor-of-base" || echo "fixer-commit NOT-ancestor-of-base"
echo "=== merge-base cdc40ae wave6-metrics ==="
git merge-base cdc40ae wave6-metrics 2>&1 | cut -c1-7
git log --oneline -1 wave6-metrics 2>&1
echo "=== RECORD.md metrics tables ==="
grep -n -i 'token\|billed\|usage table\|per-wave\|wave 6' docs/RECORD.md 2>&1 | head -20
