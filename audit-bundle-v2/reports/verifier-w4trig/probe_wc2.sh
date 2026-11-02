#!/bin/bash
# Probe J2: classify every wc mismatch; verify dump sets equal my parse.
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
PY=$ROOT/.venv/Scripts/python.exe
V=$ROOT/scratch/verifier-w4trig
cd "$ROOT" || exit 9
grep '^MISMATCH' $V/out/wc_sin.log | sed 's/.*in=\([0-9a-f]*\).*/\1/' | sort -u > $V/tmp/wc_sin_mm.txt
grep '^MISMATCH' $V/out/wc_cos.log | sed 's/.*in=\([0-9a-f]*\).*/\1/' | sort -u > $V/tmp/wc_cos_mm.txt
wc -l $V/tmp/wc_sin_mm.txt $V/tmp/wc_cos_mm.txt
cat $V/tmp/wc_cos_mm.txt
grep '^MISMATCH' $V/out/wc_cos.log | head -6
"$PY" - <<'EOF'
ROOT = "C:/Users/logan/source/repos/Muse-Softfloat"
V = ROOT + "/scratch/verifier-w4trig/tmp/"
from fractions import Fraction
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
for fn in ("sin", "cos"):
    mms = open(V + f"wc_{fn}_mm.txt").read().split()
    from collections import Counter
    print(fn, len(mms), Counter(cls64(int(h, 16)) for h in mms))
    # dump set vs own parse set
    import struct
    dump = set(int(l.strip(), 16) for l in open(V + f"wc_{fn}.dump"))
    print(fn, "dump size:", len(dump))
EOF
