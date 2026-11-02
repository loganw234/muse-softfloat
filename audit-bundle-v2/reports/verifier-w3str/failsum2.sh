#!/usr/bin/env bash
R=/c/Users/logan/source/repos/Muse-Softfloat
L=$R/scratch/verifier-w3str/replay-str.log
echo "--- fails per file:"
grep '^FAIL' "$L" | cut -d: -f1 | sort | uniq -c
echo "--- fail-line numbers per file (compact ranges):"
for f in from-decimal-str from-hex-str to-decimal-str to-hex-str; do
  echo "== $f:"
  grep "^FAIL tests/vectors/$f.vec" "$L" | sed 's/.*vec://;s/ .*//' | tr '\n' ' '
  echo
done
