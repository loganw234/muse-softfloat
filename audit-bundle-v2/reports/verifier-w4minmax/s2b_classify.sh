#!/usr/bin/env bash
# verifier-w4minmax s2b: classify replay failures by op and shape.
set -u
SCR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w4minmax
OUT=$SCR/out-replay
cd "$SCR" || exit 9
L=$OUT/replay.log
echo "== fail count by op =="
grep '^FAIL' "$L" | sed 's/.*| //' | awk '{print $1}' | sort | uniq -c | sort -rn
echo "== payload fails (all) =="
grep '^FAIL' "$L" | grep -E 'payload' | head -40
echo "payload-fail-count=$(grep -c '^FAIL.*payload' "$L")"
echo "== minmax_number single-NaN flag-only fails vs value fails =="
grep '^FAIL' "$L" | grep -E 'number' | awk '{print $NF}' | sort | uniq -c | head
echo "== sample magnitude fails =="
grep '^FAIL' "$L" | grep -E 'magnitude' | head -10
echo "== sample plain min/max fails (non-number) =="
grep '^FAIL' "$L" | grep -E 'msf[0-9]+_(minimum|maximum) ' | head -10
echo "== non-NaN zero-involved min/max fails sample =="
grep '^FAIL' "$L" | grep -E '\- (0|8000) (0|8000) ' | head -8
