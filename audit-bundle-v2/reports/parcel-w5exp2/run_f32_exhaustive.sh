#!/usr/bin/env bash
# Sharded binary32 exhaustive differential: 256 shards of
# 2^24 encodings over [0, 2^32), both functions, 11 workers.
set -u
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w5-exp2
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
OUT=/c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w5exp2/f32shards
mkdir -p "$OUT"
ulimit -v 4194304 2>/dev/null || true
echo "ulimit -v: $(ulimit -v) (KB, requested 4194304)"
echo "start: $(date '+%Y-%m-%d %H:%M:%S %z')"
EXE=build/explog/explog_exhaustive.exe
run_shard() {
    local i=$1 lo hi
    lo=$(printf '%x' $((i * 16777216)))
    hi=$(printf '%x' $(((i + 1) * 16777216)))
    "$EXE" f32 "$lo" "$hi" 2 > "$OUT/shard-$(printf '%03d' "$i").log" 2>&1
    echo "shard $i rc=$? $(date '+%H:%M:%S')"
}
running=0
for i in $(seq 0 255); do
    run_shard "$i" &
    running=$((running + 1))
    if [ "$running" -ge 11 ]; then
        wait -n
        running=$((running - 1))
    fi
done
wait
echo "all shards done: $(date '+%Y-%m-%d %H:%M:%S %z')"
grep -h 'f32 range:' "$OUT"/shard-*.log | awk '
{
  for (i=1;i<=NF;i++) {
    if ($i ~ /^checked=/) { split($i,a,"="); c+=a[2] }
    if ($i ~ /^mismatches=/) { split($i,a,"="); m+=a[2] }
    if ($i ~ /^undecided=/) { split($i,a,"="); u+=a[2] }
    if ($i ~ /^audits=/) { split($i,a,"="); au+=a[2] }
    if ($i ~ /^audit_fail=/) { split($i,a,"="); af+=a[2] }
  }
  if ($NF != "PASS") bad++
}
END { printf "AGGREGATE shards=%d checked=%.0f mismatches=%.0f undecided=%.0f audits=%.0f audit_fail=%.0f nonpass_shards=%d\n", NR, c, m, u, au, af, bad }'
grep -h 'counters:' "$OUT"/shard-*.log | awk -F'[ /]' '
{ s0+=$3; s1+=$4; s2+=$5 }
END { printf "stage hits aggregate: %.0f/%.0f/%.0f\n", s0, s1, s2 }'
grep -l 'final_undecided=[1-9]' "$OUT"/shard-*.log || echo "final_undecided: 0 in all shards"
grep -h 'MISMATCH\|UNDECIDED\|X-AUDIT-FAIL' "$OUT"/shard-*.log | head -20 || true
