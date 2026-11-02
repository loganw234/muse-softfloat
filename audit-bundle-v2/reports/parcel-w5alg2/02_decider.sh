#!/usr/bin/env bash
# 02_decider.sh - build alg_decider with hypot; sanity decides.
set -u
ulimit -v 2097152 || echo "ulimit -v unsupported here (recorded)"
WS=/c/Users/logan/source/repos/Muse-Softfloat
cd "$WS/worktrees/w5-alg2" || exit 9
S="$WS/scratch/parcel-w5alg2"
mkdir -p "$S/out" "$S/tmp"
export TMPDIR="$S/tmp"
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-w5alg2\tmp'
export TEMP="$TMP"
export MSF_PYTHON="$WS/.venv/Scripts/python.exe"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
SRC="src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c src/msf_string.c src/msf_math.c src/msf_alg.c"

echo "===== build decider ====="
gcc -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off \
  $SRC tests/alg_decider.c -o "$S/out/alg_decider.exe" -lmpfr -lgmp \
  > "$S/out/build_decider.log" 2>&1; echo "build rc=$?"
cat "$S/out/build_decider.log"

echo "===== sanity decides (expectations in comments) ====="
cat > "$S/out/sanity_in.txt" <<'EOF'
msf64_hypot 4008000000000000 4010000000000000
msf16_hypot 4200 4400
msf16_hypot 7c00 7e00
msf16_hypot 7e00 fc00
msf16_hypot 7c00 7c01
msf16_hypot 7c01 7c00
msf16_hypot 0000 8000
msf16_hypot 0001 0001
msf16_hypot 7bff 7bff
msf64_hypot 7fefffffffffffff 7fefffffffffffff
msf64_r_sqrt 3ff0000000000000
EOF
"$S/out/alg_decider.exe" decide < "$S/out/sanity_in.txt" > "$S/out/sanity_out.txt" 2>&1
echo "decide rc=$?"
cat "$S/out/sanity_out.txt"
echo "expect line1: 5.0 (4014000000000000) flags 00 x5"
echo "expect line2: hypot(3,4)=5 -> 4500 00 x5"
echo "expect line3/4: +inf 7c00 00 (inf over qNaN both orders)"
echo "expect line5/6: 7e01 01 (sNaN quieted + invalid, order cell A)"
echo "expect line7: 0 00"
echo "expect line8: sqrt2*minsub -> 1 or 2 by mode, flags 18 (underflow+inexact) te/tz/tn=1 tp=2 ta=1"
echo "===== quick differential: hseed f64 3000, h16seed 3000 ====="
time "$S/out/alg_decider.exe" hseed f64 424242 3000
echo "hseed rc=$?"
time "$S/out/alg_decider.exe" h16seed 424242 3000
echo "h16seed rc=$?"
