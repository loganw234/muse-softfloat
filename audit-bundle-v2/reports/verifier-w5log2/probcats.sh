#!/usr/bin/env bash
# pro cats.sh - categorize one-cell probe failures.
set -u
export PATH=/c/msys64/mingw64/bin:$PATH
SCR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w5log2
cd "$SCR" || exit 9
echo "--- failing cells (fmt fn hex):"
grep -oE '^[a-z0-9]+ [a-z0-9p1]+ [0-9a-f]+' logs/probes.log | sort | uniq -c | sort -rn | head -40
echo "--- total failing cell-records:"
grep -oE '^[a-z0-9]+ [a-z0-9p1]+ [0-9a-f]+' logs/probes.log | sort -u | wc -l
