#!/bin/bash
export TMPDIR="/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-sf0/tmp"
mkdir -p "$TMPDIR"
export TMP="C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-sf0/tmp"
export TEMP="C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-sf0/tmp"
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 1
B=scratch/verifier-sf0/ledger-body.txt
cp "$B" scratch/verifier-sf0/ledger-body.bak
sed -i 's/\\n/\n/g' "$B"
echo "--- after fix ---"
wc -l "$B"
grep -c "^Measured:" "$B"
grep -c "^Believed:" "$B"
grep -c "^For:" "$B"
head -8 "$B"
