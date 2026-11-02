#!/usr/bin/env bash
set -u
source "$(dirname "$0")/env.sh"
"$MSF_PYTHON" "$WS/scratch/parcel-w5aug/scripts/mutant_summary.py" "$WS/scratch/parcel-w5aug/logs/mutants"
