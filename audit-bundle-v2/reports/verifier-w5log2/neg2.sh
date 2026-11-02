#!/usr/bin/env bash
# neg2.sh - NC-POLEFLAG: scratch-mutant kernel with the pole
# DIVISION_BY_ZERO stripped; my decider must flag mismatches.
set -u
export PATH=/c/msys64/mingw64/bin:$PATH
SCR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w5log2
COPY=/c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify5-log2
ulimit -v 4194304
cd "$SCR" || exit 9
mkdir -p build/mut
cp "$COPY/src/msf_math.c" build/mut/msf_math_mut.c
# strip the two pole flag ORs (log2 +-0 pole and log2p1 -1 pole)
/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe - <<'EOF'
import re
p = 'build/mut/msf_math_mut.c'
s = open(p).read()
n = s.count('*flags |= MSF_FLAG_DIVISION_BY_ZERO;')
print('pole-flag sites found:', n)
s = s.replace('*flags |= MSF_FLAG_DIVISION_BY_ZERO;', '*flags |= 0u;')
open(p, 'w').write(s)
EOF
SRC="$COPY/src/msf16.c $COPY/src/msf32.c $COPY/src/msf64.c $COPY/src/msf_flags.c $COPY/src/msf_wide.c $COPY/src/msf_roundpack.c $COPY/src/msf_string.c $COPY/src/msf_alg.c"
# shellcheck disable=SC2086
gcc -std=c11 -O2 -ffp-contract=off -DMSF_EXPLOG_TEST_COUNTERS \
  -I"$COPY/include" -I"$COPY/src" \
  vlog2.c $SRC build/mut/msf_math_mut.c -o build/vlog2_mut.exe \
  -lmpfr -lgmp > logs/mutbuild.log 2>&1
echo "mut build rc=$?"
# duplicate-symbol check: mutant TU + real msf_math.c both define log fns?
for cell in "f64 log2 0000000000000000" "f64 log2 8000000000000000" \
  "f64 log2p1 bff0000000000000" "f32 log2p1 bf800000" "f16 log2 8000"; do
  # shellcheck disable=SC2086
  ./build/vlog2_mut.exe one $cell 2>&1 | grep -E 'MISMATCH|one:'
done
