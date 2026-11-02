#!/usr/bin/env python3
"""Check that all fuzz round-trip misses have >20 significant digits."""
import re
import sys
sys.path.insert(0, "C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w3str")
from vw_roundtrip import load
n = 0
for fn in ("C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w3str/fuzz/vw-fuzz-to-dec.vec",):
    for ln in load(fn):
        toks = ln.split()
        op = toks[0]
        if "_to_" not in op:
            continue
        fmt = "f" + op[3:].split("_to_")[0]
        a = int([t for t in toks if t.startswith("A=")][0][2:], 16)
        out = [t for t in toks if t.startswith("OUT=")][0][4:]
        spec = [t for t in toks if t.startswith("SPEC=")][0][5:]
        if out == "~":
            continue
        K = int(spec.split(",")[0])
        if K != 0 and K < {"f16": 5, "f32": 9, "f64": 17}[fmt]:
            continue
        if out.lstrip("+-") in ("nan", "snan"):
            continue
        from vw_ref import ref_from_decimal
        b, fl, c = ref_from_decimal(fmt, out, "te")
        if b != a or c != len(out):
            # count significant digits of OUT
            m = re.match(r"^(-?)(\d)(?:\.(\d+))?e([+-]\d+)$", out)
            if m:
                nd = 1 + len(m.group(3) or "")
            else:
                m2 = re.match(r"^(-?)(\d*)\.?(\d*)$", out)
                if not m2:
                    print("UNPARSEABLE", out[:80])
                    n += 1
                    continue
                nd = len((m2.group(2) + m2.group(3)).lstrip("0") or "0")
            n += 1
            if n <= 5:
                print("miss", fmt, hex(a), "K=", K, "sigdigits=", nd, out[:60])
print("total misses:", n)
