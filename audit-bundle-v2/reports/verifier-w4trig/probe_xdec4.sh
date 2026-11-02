#!/bin/bash
# Probe H4: rerun fixed mydecider, diff vs parcel decide; direct kernel
# check of a swapped/r_neg sin input (f16 0x3801).
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
PY=$ROOT/.venv/Scripts/python.exe
V=$ROOT/scratch/verifier-w4trig
C=$ROOT/worktrees/verify4-trig
cd "$ROOT" || exit 9
"$PY" $V/mydecider.py $V/tmp/xdec.in $V/tmp/xdec.my.out > $V/log_xdec_my.txt 2>&1
echo "mydecider rc=$?"
cat $V/log_xdec_my.txt
cat > $V/tmp/kcheck.c <<'EOF'
#include <stdio.h>
#include "muse_softfloat.h"
int main(void) {
    msf_flags_t fl = 0;
    /* sinPi(+0.50048828125): true +0.9999988 -> expect +1-ish (0x3c00 family) */
    msf16_t got = msf16_sin_pi((msf16_t)0x3801, 0, &fl);
    printf("kernel sin f16 3801 te -> %04x flags=%x\n", got, fl);
    return 0;
}
EOF
gcc -std=c11 -O2 -ffp-contract=off -Wno-error -I$C/include $V/tmp/kcheck.c \
  $C/src/msf16.c $C/src/msf32.c $C/src/msf64.c $C/src/msf_flags.c \
  $C/src/msf_wide.c $C/src/msf_roundpack.c $C/src/msf_string.c \
  $C/src/msf_math.c -o $V/tmp/kcheck.exe 2>/dev/null
$V/tmp/kcheck.exe
echo "=== diff my vs parcel ==="
"$PY" - <<'EOF'
ROOT = "C:/Users/logan/source/repos/Muse-Softfloat"
V = ROOT + "/scratch/verifier-w4trig/tmp/"
my = {}
for line in open(V + "xdec.my.out"):
    t = line.split()
    if t[0] == "UNDECIDED":
        continue
    my[(t[0], t[1])] = t[2:]
par = {}
n_parun = 0
for line in open(V + "xdec.parcel.out"):
    t = line.split()
    if t[0] == "UNDECIDED" or len(t) != 10:
        n_parun += 1
        continue
    par[(t[0], t[1])] = t[2:]
n_agree = n_dis = n_mine_only = 0
dis = []
for k, v in my.items():
    if k not in par:
        n_mine_only += 1
    elif [x.lower() for x in par[k]] == [x.lower() for x in v]:
        n_agree += 1
    else:
        n_dis += 1
        if len(dis) < 10:
            dis.append((k, v, par[k]))
print(f"my_decided={len(my)} agree={n_agree} disagree={n_dis} parcel-undecided={n_parun} mine-not-in-parcel={n_mine_only}")
for k, v, p in dis:
    print("DIS", k, "my=", " ".join(v), "parcel=", " ".join(p))
EOF
