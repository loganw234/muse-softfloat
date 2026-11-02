#!/bin/bash
# Probe R2: attribute every committed-vector failure to a known cell.
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
PY=$ROOT/.venv/Scripts/python.exe
V=$ROOT/scratch/verifier-w4trig
cd "$ROOT" || exit 9
grep -c '^FAIL' $V/out/verify_all.log
grep '^FAIL' $V/out/verify_all.log | sed 's/\[.*//' | sort | uniq -c | sort -rn | head
"$PY" - <<'EOF'
ROOT = "C:/Users/logan/source/repos/Muse-Softfloat"
V = ROOT + "/scratch/verifier-w4trig/"
def cls(fmt, x):
    bits = {"f16": 16, "f32": 32, "f64": 64}[fmt]
    t = {16: 10, 32: 23, 64: 52}[bits]
    emaxf = (1 << (bits - 1 - t)) - 1
    sign = (x >> (bits - 1)) & 1
    e = (x >> t) & emaxf
    frac = x & ((1 << t) - 1)
    if e == emaxf or (e == 0 and frac == 0):
        return "special-other"
    bias = (1 << (bits - 2 - t)) - 1
    sig = (frac | (1 << t)) if e else frac
    exp2 = (e - bias - t) if e else (1 - bias - t)
    if exp2 >= 0:
        return "int"
    k = -exp2
    if k >= bits:
        return "rpos"
    rem = sig & ((1 << k) - 1)
    if rem == 0:
        return "int"
    if rem == (1 << (k - 1)):
        return ("neghalf" if sign else "poshalf")
    return ("rneg" if rem > (1 << (k - 1)) else "rpos")
from collections import Counter
c = Counter()
other = []
n = 0
for line in open(V + "out/verify_all.log"):
    if not line.startswith("FAIL"):
        continue
    n += 1
    # FAIL <file:line> got <g>/<gf> want <w>/<wf> compare=.. | <op> <rm> <in> -> ...
    try:
        vec = line.split("|", 1)[1].split()
        op, rm, hx = vec[0], vec[1], vec[2]
    except Exception:
        c[("format-err", "", "")] += 1
        continue
    fmt = "f" + op.split("_")[0].replace("msf", "")
    fn = "cos" if "cos" in op else "sin"
    try:
        cl = cls(fmt, int(hx, 16))
    except Exception:
        cl = "parse-err"
    c[(fn, cl, rm)] += 1
    if (fn == "sin" and cl != "rneg") or (fn == "cos" and cl != "neghalf"):
        other.append(line.strip())
print("total FAIL lines:", n)
for k in sorted(c):
    print(k, c[k])
print("non-sign-cell failures:", len(other))
for l in other[:10]:
    print("OTHER:", l)
EOF
