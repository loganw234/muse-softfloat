#!/usr/bin/env bash
set -euo pipefail
cd /c/Users/logan/source/repos/Muse-Softfloat
mkdir -p scratch/verifier-phase0/tmp
export TMPDIR=$PWD/scratch/verifier-phase0/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\verifier-phase0\tmp'
export TEMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\verifier-phase0\tmp'
bash softfloat-bootstrap-kit/tools/ledger.sh append ledger verifier-phase0 "verifier-phase0 started: commit aec2295 read before lead ledger" < scratch/verifier-phase0/body-start.txt
