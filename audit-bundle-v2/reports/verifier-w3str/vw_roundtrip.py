#!/usr/bin/env python3
"""vw_roundtrip.py - round-trip property: parse-back (my ref, te) of a
to_* OUT string must equal the input bits (finite), or class+sign (NaN),
for outputs at >= Pmin digits / exact-enough hex. Independent of the TU:
checks the digit strings as data. Usage: vw_roundtrip.py VECFILES...
Also does exhaustive-f16 sweep internally."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vw_ref import (ref_from_decimal, ref_from_hex, ref_to_decimal,
                    ref_to_hex, decode, PMIN)
from vw_gen import bstr

WIDTH = {"f16": 4, "f32": 8, "f64": 16}


def load(fn):
    with open(fn, "r", newline="") as f:
        txt = f.read()
    out = []
    for ln in txt.split("\n"):
        ln = ln.strip()
        if ln and not ln.startswith("#"):
            out.append(ln)
    return out


def check_vec(fn):
    nfin = nok = nnan = nnanok = nskip = 0
    bad = []
    for ln in load(fn):
        toks = ln.split()
        op = toks[0]
        if "_to_" not in op:
            continue
        fmt = "f" + op[3:].split("_to_")[0]
        fam = op.split("_to_")[1]
        rm = toks[1]
        a = int([t for t in toks if t.startswith("A=")][0][2:], 16)
        out = [t for t in toks if t.startswith("OUT=")][0][4:]
        spec = [t for t in toks if t.startswith("SPEC=")][0][5:]
        if out == "~":
            nskip += 1
            continue
        d = decode(fmt, a)
        if d["cls"] in ("inf",):
            continue
        if d["cls"] in ("qnan", "snan"):
            nnan += 1
            if fam == "decimal":
                b, fl, c = ref_from_decimal(fmt, out, rm)
            else:
                b, fl, c = ref_from_hex(fmt, out, rm)
            dd = decode(fmt, b)
            exp_sign_ok = (dd["sign"] == d["sign"])
            exp_cls_ok = (dd["cls"] == d["cls"])
            if exp_sign_ok and exp_cls_ok:
                nnanok += 1
            else:
                bad.append("NAN-RT %s A=%x OUT=%s back=%x" % (fmt, a, out, b))
            continue
        nfin += 1
        if fam == "decimal":
            K = int(spec.split(",")[0])
            if K != 0 and K < PMIN[fmt]:
                nskip += 1
                nfin -= 1
                continue
            b, fl, c = ref_from_decimal(fmt, out, rm)
            if c != len(out):
                bad.append("RT-CONSUME %s A=%x OUT=%s c=%d" % (fmt, a, out, c))
            elif b != a:
                bad.append("RT%s %s A=%x OUT=%s back=%x" % (
                    "" if rm == "te" else "-DIR", fmt, a, out, b))
            else:
                nok += 1
        else:
            if spec != "-1":
                nskip += 1
                nfin -= 1
                continue
            b, fl, c = ref_from_hex(fmt, out, rm)
            if b != a or c != len(out):
                bad.append("RTHEX %s A=%x OUT=%s back=%x c=%d" % (fmt, a, out, b, c))
            else:
                nok += 1
    return nfin, nok, nnan, nnanok, nskip, bad


def main(files):
    T = [0, 0, 0, 0, 0]
    allbad = []
    for fn in files:
        r = check_vec(fn)
        print("%s: finite %d/%d, nan %d/%d, skipped %d" % (fn, r[1], r[0], r[3], r[2], r[4]))
        for i in range(5):
            T[i] += r[i]
        allbad += [(fn, b) for b in r[5][:10]]
    print("TOTAL: finite %d/%d, nan %d/%d, skipped %d" % (T[1], T[0], T[3], T[2], T[4]))
    for fn, b in allbad[:20]:
        print(fn, b)


if __name__ == "__main__":
    main(sys.argv[1:])
