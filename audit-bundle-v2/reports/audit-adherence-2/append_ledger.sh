#!/usr/bin/env bash
set -eu
cd "$(dirname "$0")/../.." || exit 2
export TMPDIR="$PWD/scratch/audit-adherence-2/tmp"
mkdir -p "$TMPDIR"
export TMP="$(cygpath -m "$TMPDIR")"
export TEMP="$TMP"
bash softfloat-bootstrap-kit/tools/ledger.sh append ledger auditor-adherence-2 \
  "Whole-project methods audit: ADHERENT WITH SLIPS at 7c3819c" \
  < scratch/audit-adherence-2/ledger-body.txt
echo "append exit=$?"
