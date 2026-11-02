#!/usr/bin/env bash
# runprobes.sh - execute one-cell probes, collect verdicts.
set -u
export PATH=/c/msys64/mingw64/bin:$PATH
SCR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w5log2
ulimit -v 4194304
cd "$SCR" || exit 9
tail -n +2 logs/cells.txt > logs/celllist.txt
wc -l logs/celllist.txt
: > logs/probes.log
pass=0; fail=0
while read -r fmt fn hx; do
  out=$(./build/vlog2.exe one "$fmt" "$fn" "$hx" 2>&1)
  line=$(echo "$out" | tail -1)
  case "$line" in
    *PASS) pass=$((pass+1)) ;;
    *) fail=$((fail+1)); echo "$fmt $fn $hx :: $out" >> logs/probes.log ;;
  esac
done < logs/celllist.txt
echo "probe cells: pass=$pass fail=$fail"
grep -c . logs/probes.log
