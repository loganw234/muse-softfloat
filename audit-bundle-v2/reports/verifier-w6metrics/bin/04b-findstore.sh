#!/bin/bash
# Find session-store paths named in prior verifier scripts/reports.
set -u
ROOT="C:/Users/logan/source/repos/Muse-Softfloat"
grep -rhoE '[A-Za-z]:/[^ "'\'')]*subagent[^ "'\'')]*' "$ROOT/scratch/verifier-w5metrics/"*.sh "$ROOT/scratch/verifier-w5metrics/"*.py "$ROOT/scratch/verifier-w5metrics/report.md" 2>/dev/null | sort -u | head -10
echo "=== session.jsonl path mentions ==="
grep -rhoE '[A-Za-z]:/[^ "'\'')]*session\.jsonl' "$ROOT/scratch/verifier-w5metrics/"*.sh "$ROOT/scratch/verifier-w5metrics/"*.py 2>/dev/null | sort -u | head -10
echo "=== STORE|store dir mentions ==="
grep -rhoE '(STORE|store|SESSION)[A-Za-z_]*=[^ ;]*' "$ROOT/scratch/verifier-w5metrics/"*.sh 2>/dev/null | sort -u | head -10
echo "=== any DIR= assignments ==="
grep -rhE '^[A-Za-z_]+="?[A-Za-z]:/' "$ROOT/scratch/verifier-w5metrics/"*.sh 2>/dev/null | sort -u | head -20
