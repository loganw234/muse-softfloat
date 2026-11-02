#!/bin/bash
# Probe J3: raised-cap vehicle (scratch copy of the harness with the
# 20-line print cap lifted; logic untouched) for full mismatch-set
# analysis of the sin worst-case gate.
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
PY=$ROOT/.venv/Scripts/python.exe
V=$ROOT/scratch/verifier-w4trig
C=$ROOT/worktrees/verify4-trig
OR=$ROOT/scratch/oracles/core-math-3b2163bb87c222c7db17a721425fbef31e98fd94/src/binary64
cd "$ROOT" || exit 9
sed 's/if (g_mismatch <= 20)/if (g_mismatch <= 100000000)/' \
  $C/tests/trig_exhaustive.c > $V/tmp/trigx_full.c
grep -c 'g_mismatch <= 100000000' $V/tmp/trigx_full.c
gcc -std=c11 -O2 -Wall -ffp-contract=off -Wno-error \
  -DMSF_TRIG_TEST_COUNTERS \
  -I$C/include -I$C/src \
  $V/tmp/trigx_full.c \
  $C/src/msf16.c $C/src/msf32.c $C/src/msf64.c $C/src/msf_flags.c \
  $C/src/msf_wide.c $C/src/msf_roundpack.c $C/src/msf_string.c \
  $C/src/msf_math.c \
  -lmpfr -lgmp -o $V/tmp/trigx_full.exe 2>&1 | head -3
echo "full vehicle build rc=$?"
$V/tmp/trigx_full.exe wc sin $OR/sinpi/sinpi.wc > $V/out/wc_sin_full.log 2>&1
echo "wc sin full rc=$?"
tail -2 $V/out/wc_sin_full.log
"$PY" - <<'EOF'
ROOT = "C:/Users/logan/source/repos/Muse-Softfloat"
V = ROOT + "/scratch/verifier-w4trig/"
from collections import Counter
def cls64(x):
    sign = (x >> 63) & 1
    e = (x >> 52) & 0x7FF
    frac = x & ((1 << 52) - 1)
    if e == 0x7FF:
        return "nonfinite"
    if e == 0:
        return "zero" if frac == 0 else "sub"
    sig = frac | (1 << 52)
    exp2 = e - 1023 - 52
    if exp2 >= 0:
        return "int"
    k = -exp2
    rem = sig & ((1 << k) - 1)
    if rem == 0:
        return "int"
    if rem == (1 << (k - 1)):
        return ("neghalf" if sign else "poshalf")
    if rem > (1 << (k - 1)):
        return "rneg"
    return "rpos"
mm = {}
for line in open(V + "out/wc_sin_full.log"):
    if not line.startswith("MISMATCH"):
        continue
    t = line.split()
    assert len(t) == 7, line
    fn, rm, hx, got, want = t[2], t[3], t[4][3:], t[5][4:], t[6][5:]
    mm.setdefault(int(hx, 16), []).append((rm, got, want))
print("mismatching inputs:", len(mm), "lines:", sum(len(v) for v in mm.values()))
print(Counter(cls64(x) for x in mm))
# every mismatching input must mismatch in exactly 4 modes with a pure sign flip
import sys
bad = 0
shown = 0
for x, lst in mm.items():
    if len(lst) != 4:
        bad += 1
        if shown < 5:
            print("NOT4", hex(x), lst)
            shown += 1
        continue
    for rm, got, want in lst:
        g, w = int(got.split("/")[0], 16), int(want.split("/")[0], 16)
        if g ^ w != (1 << 63):
            bad += 1
            if shown < 5:
                print("NOTSIGNFLIP", hex(x), lst)
                shown += 1
            break
print("non-conforming entries:", bad)
# dump set == parsed set?
dump = set(int(l.strip(), 16) for l in open(V + "tmp/wc_sin.dump"))
print("dump size:", len(dump))
EOF
