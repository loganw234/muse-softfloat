#!/bin/bash
# Probe H3: characterize mydecider UNDECIDED inputs; diff vs parcel decide.
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
PY=$ROOT/.venv/Scripts/python.exe
V=$ROOT/scratch/verifier-w4trig
cd "$ROOT" || exit 9
grep '^UNDECIDED' $V/tmp/xdec.my.out | sed 's/.*cos_pi \([0-9a-f]*\).*/\1/' > $V/tmp/undec.hex
"$PY" - <<'EOF'
import struct, math
ROOT = "C:/Users/logan/source/repos/Muse-Softfloat"
hexes = open(ROOT + "/scratch/verifier-w4trig/tmp/undec.hex").read().split()
print("n =", len(hexes))
classes = {"subnormal": 0, "tiny-exp": 0, "normal": 0}
exps = []
for h in hexes:
    b = int(h, 16)
    d = struct.unpack("<d", struct.pack("<Q", b))[0]
    e = (b >> 52) & 0x7FF
    if e == 0:
        classes["subnormal"] += 1
    else:
        exps.append(e - 1023)
        if e - 1023 < -60:
            classes["tiny-exp"] += 1
        else:
            classes["normal"] += 1
print(classes)
import statistics
print("exp min/max of normals:", min(exps), max(exps))
# histogram of true exponents
from collections import Counter
print(Counter((e // 64) * 64 for e in exps).most_common(8))
EOF
echo "=== diff my vs parcel (decided lines only) ==="
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
for line in open(V + "xdec.parcel.out"):
    t = line.split()
    if t[0] == "UNDECIDED" or len(t) != 10:
        par[(t[0], t[1])] = None
        continue
    par[(t[0], t[1])] = t[2:]
n_agree = n_dis = n_parun = 0
dis = []
for k, v in my.items():
    if k not in par or par[k] is None:
        n_parun += 1
    elif [x.lower() for x in par[k]] == [x.lower() for x in v]:
        n_agree += 1
    else:
        n_dis += 1
        if len(dis) < 10:
            dis.append((k, v, par[k]))
print(f"agree={n_agree} disagree={n_dis} parcel-undecided-or-missing={n_parun}")
for k, v, p in dis:
    print("DIS", k, "my=", " ".join(v), "parcel=", " ".join(p))
EOF
