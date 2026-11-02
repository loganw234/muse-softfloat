#!/usr/bin/env bash
export TMPDIR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-wave0/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\verifier-wave0\tmp'
export TEMP="$TMP"
mkdir -p "$TMPDIR"
cd /c/Users/logan/source/repos/Muse-Softfloat
bash softfloat-bootstrap-kit/tools/ledger.sh append ledger verifier-wave0 "verdict NOT READY on 4805d2e: two (b)s, both restatable in place before push" < scratch/verifier-wave0/ledger_body.txt
echo "exit=$?"
tail -n 12 ledger/verifier-wave0.md
