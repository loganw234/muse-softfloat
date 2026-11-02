#!/usr/bin/env bash
# probe3 replay: run copy's runner over all p3 vectors, summarize per family
set -u
S=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w1f32
export PATH=/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH
cd "$S" || exit 9
RUN="$S/msf_runner.exe"
: > p3-summary.log
total_f=0
for f in p3/p3-*.vec; do
  base=$(basename "$f")
  log="p3-verify-${base%.vec}.log"
  "$RUN" verify "$f" > "$log" 2>&1
  rc=$?
  fails=$(grep -c '^FAIL' "$log" || true)
  cases=$(grep -c -v '^#' "$f" || true)
  echo "$base: cases=$cases exit=$rc fails=$fails" | tee -a p3-summary.log
done
echo done-p3replay
