#!/usr/bin/env bash
# s_berk1.sh - Berkeley level-1 complete sweeps for all applicable fns/modes
set -u
CP="C:/Users/logan/source/repos/Muse-Softfloat/worktrees/verify2-f16"
SC="C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w2f16"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export MSF_TESTFLOAT_GEN="C:/Users/logan/source/repos/Muse-Softfloat/scratch/oracles/TestFloat-3e/build/Linux-x86_64-GCC/testfloat_gen.exe"
export MSF_PYTHON="C:/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe"
cd "$CP" || exit 9
mkdir -p "$SC/berk1"
R="build/smoke/msf_runner.exe"
run_one() {
  fn="$1"; rm="$2"; tag="$3"
  out="$SC/berk1/${tag}.vec"
  "$MSF_PYTHON" tests/berkeley_ingest.py --fn "$fn" --rm "$rm" --level 1 --out "$out" >> "$SC/berk1-ingest.log" 2>&1
  n=$(grep -vc '^#' "$out")
  res=$("$R" verify "$out" 2>&1 | grep -E '^(total|VERDICT)' | tr '\n' ' ')
  echo "$tag n=$n $res"
}
: > "$SC/berk1-ingest.log"
for fn in f16_add f16_sub f16_mul f16_div f16_sqrt; do
  for rm in te tz tp tn ta; do
    run_one "$fn" "$rm" "${fn}-${rm}-l1"
  done
done 2>&1 | tee "$SC/berk1-arith.log"
run_one f16_rem - "f16_rem-l1" 2>&1 | tee -a "$SC/berk1-arith.log"
for rm in te tz tp tn ta; do
  run_one f16_mulAdd "$rm" "f16_mulAdd-${rm}-l1"
done 2>&1 | tee -a "$SC/berk1-arith.log"
for rm in te tz tp tn ta; do
  run_one f16_roundToInt "$rm" "f16_roundToInt-${rm}-l1"
done 2>&1 | tee "$SC/berk1-rint.log"
for rm in te tz tp tn ta; do
  run_one f16_to_f16 "$rm" "f16_to_f16-${rm}-l1"
  run_one f32_to_f16 "$rm" "f32_to_f16-${rm}-l1"
  run_one f64_to_f16 "$rm" "f64_to_f16-${rm}-l1"
  for c in i32 i64 ui32 ui64; do
    run_one "${c}_to_f16" "$rm" "${c}_to_f16-${rm}-l1"
    run_one "f16_to_${c}" "$rm" "f16_to_${c}-${rm}-l1"
  done
done 2>&1 | tee "$SC/berk1-conv.log"
for fn in f16_eq f16_eq_signaling f16_le f16_lt f16_le_quiet f16_lt_quiet; do
  run_one "$fn" - "${fn}-l1"
done 2>&1 | tee "$SC/berk1-cmp.log"
echo ALLDONE
