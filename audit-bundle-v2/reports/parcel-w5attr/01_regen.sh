#!/usr/bin/env bash
# w5-attr regeneration: seam + directed vector sets (Git Bash).
set -u
WS=/c/Users/logan/source/repos/Muse-Softfloat
cd "$WS/worktrees/w5-attr" || exit 9
S="$WS/scratch/parcel-w5attr"
mkdir -p "$S/out" "$S/tmp"
export TMPDIR="$S/tmp"
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-w5attr\tmp'
export TEMP="$TMP"
export MSF_PYTHON="$WS/.venv/Scripts/python.exe"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
PY="$MSF_PYTHON"
echo "python: $PY ($($PY --version 2>&1))"
gcc -dumpmachine; gcc -dumpversion

echo "===== gen_tables (seam) ====="
"$PY" tools/gen_tables.py > "$S/out/gen_tables.log" 2>&1; echo "gen_tables rc=$?"
cat "$S/out/gen_tables.log"

echo "===== directed generators ====="
for g in gen_vectors gen_vectors_f16 gen_vectors_f32 gen_vectors_f64 gen_vectors_xf gen_vectors_str; do
  "$PY" "tests/$g.py" directed tests/vectors > "$S/out/gen_$g.log" 2>&1
  echo "$g directed rc=$?"; tail -3 "$S/out/gen_$g.log"
done

echo "===== trig decider build + trig vectors ====="
SRC="src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c src/msf_string.c src/msf_math.c"
gcc -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off -DMSF_TRIG_TEST_COUNTERS \
  $SRC tests/trig_exhaustive.c -o "$S/out/trig_exhaustive.exe" -lmpfr -lgmp \
  > "$S/out/build_trig_decider.log" 2>&1
echo "trig decider build rc=$?"; cat "$S/out/build_trig_decider.log"
export MSF_TRIG_DECIDER="$S/out/trig_exhaustive.exe"
"$PY" tests/gen_vectors_trig.py tests/vectors > "$S/out/gen_trig.log" 2>&1
echo "gen_trig rc=$?"; cat "$S/out/gen_trig.log"

echo "===== counts ====="
"$PY" "$S/counts.py" tests/vectors > "$S/out/counts.log" 2>&1; echo "counts rc=$?"
cat "$S/out/counts.log"
echo "===== regen done ====="
