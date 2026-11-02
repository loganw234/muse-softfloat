#!/usr/bin/env bash
# probe2: independent Berkeley differential vs pinned testfloat_gen.
# Streams level-1 complete per brief, ingests, replays with copy's runner.
set -u
W=/c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify-f32
S=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w1f32
export PATH=/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH
PY=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
export MSF_TESTFLOAT_GEN=C:/Users/logan/source/repos/Muse-Softfloat/scratch/oracles/TestFloat-3e/build/Linux-x86_64-GCC/testfloat_gen.exe
cd "$W" || exit 9
B="$S/berkeley"
rm -rf "$B"
mkdir -p "$B/vecs"
RUN="$S/msf_runner.exe"
SUM="$B/summary.log"
: > "$SUM"
total_cases=0
total_fail=0
run_one() { # fn rm take
  fn="$1"; rm="$2"; take="$3"
  tag="${fn}-${rm}-l1"
  out="$B/vecs/${tag}.vec"
  "$PY" tests/berkeley_ingest.py --fn "$fn" --rm "$rm" --level 1 --take "$take" --out "$out" > "$B/vecs/${tag}.gen.log" 2>&1
  if [ $? -ne 0 ]; then echo "$tag: INGEST-FAILED" | tee -a "$SUM"; return; fi
  n=$(grep -c -v '^#' "$out")
  log="$B/vecs/${tag}.verify.log"
  "$RUN" verify "$out" > "$log" 2>&1
  rc=$?
  fails=$(grep -c '^FAIL' "$log" || true)
  echo "$tag: cases=$n runner_exit=$rc fails=$fails" | tee -a "$SUM"
  if [ "$fails" != "0" ]; then grep '^FAIL' "$log" | head -n 10; fi
}
echo "=== big four + sqrt + rem, all 5 modes ===" | tee -a "$SUM"
for op in add sub mul div sqrt; do
  for rm in te tz tp tn ta; do
    run_one "f32_$op" "$rm" 0
  done
done
run_one f32_rem - 0
echo "=== mulAdd te/ta take 500000 ===" | tee -a "$SUM"
run_one f32_mulAdd te 500000
run_one f32_mulAdd ta 500000
echo "=== conversions level 1 (all rms) ===" | tee -a "$SUM"
for fn in f32_to_i32 f32_to_i64 f32_to_ui32 f32_to_ui64 i32_to_f32 i64_to_f32 ui32_to_f32 ui64_to_f32 f64_to_f32 f32_roundToInt; do
  for rm in te tz tp tn ta; do
    run_one "$fn" "$rm" 0
  done
done
echo "=== comparisons level 1 ===" | tee -a "$SUM"
for fn in f32_eq f32_eq_signaling f32_le f32_lt f32_le_quiet f32_lt_quiet; do
  run_one "$fn" - 0
done
echo done-probe2
