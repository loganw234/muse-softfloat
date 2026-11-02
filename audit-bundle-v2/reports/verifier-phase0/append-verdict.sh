#!/usr/bin/env bash
set -euo pipefail
cd /c/Users/logan/source/repos/Muse-Softfloat
mkdir -p scratch/verifier-phase0/tmp
export TMPDIR=$PWD/scratch/verifier-phase0/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\verifier-phase0\tmp'
export TEMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\verifier-phase0\tmp'
bash softfloat-bootstrap-kit/tools/ledger.sh append ledger verifier-phase0 "verdict NOT READY on aec2295: two (b) text defects plus absolute home paths for a public push" < scratch/verifier-phase0/body-verdict.txt
