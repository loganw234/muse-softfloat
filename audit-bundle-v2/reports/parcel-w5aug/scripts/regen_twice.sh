#!/usr/bin/env bash
set -eu
source "$(dirname "$0")/env.sh"
"$MSF_PYTHON" tools/gen_tables.py > "$WS/scratch/parcel-w5aug/logs/regen1.log" 2>&1
sha256sum include/muse_softfloat.h src/msf_formats.h tests/msf_dispatch.h docs/COVERAGE.tsv > "$WS/scratch/parcel-w5aug/logs/regen1.sha"
"$MSF_PYTHON" tools/gen_tables.py > "$WS/scratch/parcel-w5aug/logs/regen2.log" 2>&1
sha256sum include/muse_softfloat.h src/msf_formats.h tests/msf_dispatch.h docs/COVERAGE.tsv > "$WS/scratch/parcel-w5aug/logs/regen2.sha"
cmp "$WS/scratch/parcel-w5aug/logs/regen1.sha" "$WS/scratch/parcel-w5aug/logs/regen2.sha"
cmp "$WS/scratch/parcel-w5aug/logs/regen1.log" "$WS/scratch/parcel-w5aug/logs/regen2.log"
echo "regen twice: byte-stable"
cat "$WS/scratch/parcel-w5aug/logs/regen1.log"
cat "$WS/scratch/parcel-w5aug/logs/regen1.sha"
