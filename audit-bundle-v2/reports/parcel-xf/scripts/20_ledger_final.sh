#!/usr/bin/env bash
set -euo pipefail
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
export TMPDIR="$ROOT/scratch/parcel-xf/tmp"
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-xf\tmp'
export TEMP="$TMP"
bash "$ROOT/softfloat-bootstrap-kit/tools/ledger.sh" append "$ROOT/ledger" parcel-xf \
  "READY: 126 xf rows gated green (2.91M xf vectors), head 7935fab unpushed" \
  < "$ROOT/scratch/parcel-xf/final-ledger-body.md"
echo OK
cd "$ROOT/worktrees/w2-xf" || exit 9
git -c safe.directory="$PWD" status --porcelain
git -c safe.directory="$PWD" log --oneline dd48b08..HEAD
