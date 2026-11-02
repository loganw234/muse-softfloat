#!/usr/bin/env bash
set -u
WS=/c/Users/logan/source/repos/Muse-Softfloat
cd "$WS/worktrees/w5-attr" || exit 9
S="$WS/scratch/parcel-w5attr"
mkdir -p "$S/out/exh" "$S/out/ctrl" "$S/tmp"
export TMPDIR="$S/tmp"
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-w5attr\tmp'
export TEMP="$TMP"
export MSF_PYTHON="$WS/.venv/Scripts/python.exe"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
PY="$MSF_PYTHON"
R=build/smoke/msf_runner.exe
SRC="src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c src/msf_math.c"

echo "===== f16 exhaustive (gen_vectors_f16, five modes) ====="
"$PY" tests/gen_vectors_f16.py exhaustive "$S/out/exh" > "$S/out/exh/gen_f16.log" 2>&1
echo "gen rc=$?"; ls "$S/out/exh"
grep -c " ta " "$S/out/exh"/*.vec || true
"$R" verify "$S/out/exh"/ex-*.vec > "$S/out/exh/verify_f16.log" 2>&1
echo "verify rc=$?"; grep -E '^(file|total|VERDICT)' "$S/out/exh/verify_f16.log"

echo "===== xf exhaustive-f16 (conv + sqrt te/tp/tn/ta) ====="
"$PY" tests/gen_vectors_xf.py exhaustive-f16 "$S/out/exh/xf-exh.vec" > "$S/out/exh/gen_xf.log" 2>&1
echo "gen rc=$?"
grep -c " ta " "$S/out/exh/xf-exh.vec" || true
"$R" verify "$S/out/exh/xf-exh.vec" > "$S/out/exh/verify_xf.log" 2>&1
echo "verify rc=$?"; grep -E '^(total|VERDICT)' "$S/out/exh/verify_xf.log"

echo "===== trig f16 exhaustive relabel stream ====="
"$PY" "$S/make_trig_relabel_f16.py" "$S/out/trig_exhaustive.exe" "$S/out/exh/trig-f16-relabel.vec" > "$S/out/exh/gen_trig_relabel.log" 2>&1
echo "gen rc=$?"; cat "$S/out/exh/gen_trig_relabel.log"
"$R" verify "$S/out/exh/trig-f16-relabel.vec" > "$S/out/exh/verify_trig_relabel.log" 2>&1
echo "verify rc=$?"; grep -E '^(total|VERDICT)' "$S/out/exh/verify_trig_relabel.log"

echo "===== str bulk five-mode differentials ====="
for kind in from-decimal to-decimal from-hex to-hex; do
  "$PY" tests/gen_vectors_str.py bulk "$kind" "$S/out/exh/bulk-$kind.vec" 20000 20261028 > "$S/out/exh/gen_bulk_$kind.log" 2>&1
  echo "gen $kind rc=$? ta lines: $(grep -c ' ta ' "$S/out/exh/bulk-$kind.vec")"
done
"$R" verify "$S/out/exh"/bulk-*.vec > "$S/out/exh/verify_bulk.log" 2>&1
echo "verify rc=$?"; grep -E '^(total|VERDICT)' "$S/out/exh/verify_bulk.log"

echo "===== controls preparation ====="
"$PY" "$S/make_controls.py" "$PWD" "$S/out/ctrl" > "$S/out/ctrl/make.log" 2>&1
echo "make rc=$?"; cat "$S/out/ctrl/make.log"

echo "===== sqrt relabel replay (must PASS) ====="
"$R" verify "$S/out/ctrl/sqrt_relabel.vec" > "$S/out/ctrl/verify_sqrt_relabel.log" 2>&1
echo "verify rc=$?"; grep -E '^(total|VERDICT)' "$S/out/ctrl/verify_sqrt_relabel.log"

echo "===== control (a) ta->tz in dec_round_inc only (must FAIL) ====="
gcc -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off -DMSF_BUILD_ID='"mutant-dec"' \
  $SRC "$S/out/ctrl/msf_string_mutant_dec.c" tests/runner.c tests/sha256.c \
  -o "$S/out/ctrl/runner_mutant_dec.exe" > "$S/out/ctrl/build_dec.log" 2>&1
echo "build rc=$?"; cat "$S/out/ctrl/build_dec.log"
"$S/out/ctrl/runner_mutant_dec.exe" verify tests/vectors/to-decimal-str.vec tests/vectors/from-decimal-str.vec > "$S/out/ctrl/verify_mutant_dec.log" 2>&1
echo "mutant-dec verify rc=$? (nonzero required)"
grep -E '^(total|VERDICT)' "$S/out/ctrl/verify_mutant_dec.log"; grep -m3 '^FAIL' "$S/out/ctrl/verify_mutant_dec.log" || true

echo "===== control (a2) ta->tz in to_hex only (must FAIL) ====="
gcc -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off -DMSF_BUILD_ID='"mutant-hex"' \
  $SRC "$S/out/ctrl/msf_string_mutant_hex.c" tests/runner.c tests/sha256.c \
  -o "$S/out/ctrl/runner_mutant_hex.exe" > "$S/out/ctrl/build_hex.log" 2>&1
echo "build rc=$?"
"$S/out/ctrl/runner_mutant_hex.exe" verify tests/vectors/to-hex-str.vec > "$S/out/ctrl/verify_mutant_hex.log" 2>&1
echo "mutant-hex verify rc=$? (nonzero required)"
grep -E '^(total|VERDICT)' "$S/out/ctrl/verify_mutant_hex.log"; grep -m3 '^FAIL' "$S/out/ctrl/verify_mutant_hex.log" || true

echo "===== control (b) te/ta swap on arith-f32 (must FAIL) ====="
awk '{if($2=="te")$2="ta"; else if($2=="ta")$2="te"} {print}' tests/vectors/arith-f32.vec > "$S/out/ctrl/wrongrm-ta.vec"
"$R" verify "$S/out/ctrl/wrongrm-ta.vec" > "$S/out/ctrl/verify_wrongrm_ta.log" 2>&1
echo "wrongrm verify rc=$? (nonzero required)"
grep -E '^(total|VERDICT)' "$S/out/ctrl/verify_wrongrm_ta.log"

echo "===== control (c) flipped relabeled trig line (must FAIL) ====="
"$R" verify "$S/out/ctrl/trig_flipped.vec" > "$S/out/ctrl/verify_trig_flipped.log" 2>&1
echo "flipped verify rc=$? (nonzero required)"
grep -E '^(total|VERDICT)' "$S/out/ctrl/verify_trig_flipped.log"; grep -m2 '^FAIL' "$S/out/ctrl/verify_trig_flipped.log" || true
echo "===== 05 done ====="
