#!/usr/bin/env bash
# stage_ledger.sh - append the verifier-w2xf entry via the kit tool
set -u
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
export TMPDIR="$ROOT/scratch/verifier-w2xf/tmp"
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\verifier-w2xf\tmp'
export TEMP="$TMP"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
/usr/bin/bash "$ROOT/softfloat-bootstrap-kit/tools/ledger.sh" append \
  "$ROOT/ledger" verifier-w2xf \
  "NOT READY: wave-2 cross-format copy, 3 wrapper defects plus vector and regen findings" \
  < "$ROOT/scratch/verifier-w2xf/ledger-body.md"
echo "ledger exit=$?"
tail -3 "$ROOT/ledger/verifier-w2xf.md"
