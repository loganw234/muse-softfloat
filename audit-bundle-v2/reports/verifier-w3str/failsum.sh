#!/usr/bin/env bash
R=/c/Users/logan/source/repos/Muse-Softfloat
L=$R/scratch/verifier-w3str/replay-str.log
echo "--- fails by op+mode:"
grep '^FAIL' "$L" | cut -d' ' -f1,2 | sort | uniq -c | sort -rn | head -30
echo "--- fails by provenance tag:"
grep '^FAIL' "$L" | grep -o 'want.*' | head -5
echo "--- sample FAIL lines:"
grep '^FAIL' "$L" | head -12
