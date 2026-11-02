#!/usr/bin/env python3
"""vw_check_committed.py - run vw_ref over the copy's committed str vectors,
compare with committed expectations. Triangulates my reference vs parcel data.
Usage: vw_check_committed.py <vecdir> ; prints mismatch lines + summary."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vw_ref import ref_from_decimal, ref_from_hex, ref_to_decimal, ref_to_hex

WIDTH = {"f16": 4, "f32": 8, "f64": 16}
FMAP = {"16": "f16", "32": "f32", "f64": "f64"}


def load(fn):
    with open(fn, "r", newline="") as f:
        txt = f.read()
    txt = txt.replace("\\\r\n", "").replace("\\\n", "")
    lines = []
    for ln in txt.split("\n"):
        ln = ln.strip()
        if ln == "" or ln.startswith("#"):
            continue
        lines.append(ln)
    return lines


def bits_str(b, fmt):
    return "%0*x" % (WIDTH[fmt], b)


def main(vdir):
    ntot = nok = 0
    bad = []
    for fn in ("from-decimal-str.vec", "from-hex-str.vec",
               "to-decimal-str.vec", "to-hex-str.vec"):
        for ln in load(os.path.join(vdir, fn)):
            toks = ln.split()
            op = toks[0]
            assert op.startswith("msf"), ln
            rest = op[3:]
            if "_from_" in rest:
                fmt = "f" + rest.split("_from_")[0]
                fam = rest.split("_from_")[1]
                rm = toks[1]
                intrans = [t for t in toks if t.startswith("IN=")][0][3:]
                s = "" if intrans == "~" else intrans
                arrow = toks.index("->")
                wbits = toks[arrow + 1].lower()
                wflags = int(toks[arrow + 2], 16)
                wc = int([t for t in toks if t.startswith("C=")][0][2:])
                if fam == "decimal":
                    b, fl, c = ref_from_decimal(fmt, s, rm)
                else:
                    b, fl, c = ref_from_hex(fmt, s, rm)
                ntot += 1
                if bits_str(b, fmt) == wbits and fl == wflags and c == wc:
                    nok += 1
                else:
                    bad.append("MISMATCH %s:%s\n  mine: -> %s %02x C=%d\n  vec : %s" %
                               (fn, ln[:100], bits_str(b, fmt), fl, c, ln[:160]))
            else:
                fmt = "f" + rest.split("_to_")[0]
                fam = rest.split("_to_")[1]
                rm = toks[1]
                a = int([t for t in toks if t.startswith("A=")][0][2:], 16)
                spec = [t for t in toks if t.startswith("SPEC=")][0][5:]
                out = [t for t in toks if t.startswith("OUT=")][0][4:]
                wlen = int([t for t in toks if t.startswith("LEN=")][0][4:])
                arrow = toks.index("->")
                wflags = int(toks[arrow - 2] if toks[arrow - 1].startswith("LEN=") else toks[arrow - 1], 16)
                # flags token sits right before provenance: toks[-2]
                wflags = int(toks[-2], 16)
                if fam == "decimal":
                    p, st, mn = [int(x) for x in spec.split(",")]
                    o, L, fl = ref_to_decimal(fmt, a, p, st, mn, rm)
                else:
                    o, L, fl = ref_to_hex(fmt, a, int(spec), rm)
                ntot += 1
                if o == out and L == wlen and fl == wflags:
                    nok += 1
                else:
                    bad.append("MISMATCH %s\n  mine: OUT=%s LEN=%d %02x\n  vec : %s" % (ln[:120], o, L, fl, ln[:200]))
    print("committed-vs-myref: %d/%d agree, %d differ" % (nok, ntot, ntot - nok))
    for b in bad[:60]:
        print(b)
    if len(bad) > 60:
        print("... and %d more" % (len(bad) - 60))


if __name__ == "__main__":
    main(sys.argv[1])
