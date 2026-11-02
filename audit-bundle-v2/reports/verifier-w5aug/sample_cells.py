#!/usr/bin/env python3
"""sample_cells.py - verifier-w5aug: emit a small pair-vector file of
cells where the copy's kernel is KNOWN correct (myref == kernel, proved
by the committed runner verify PASS below), for the fake-serial board
plumbing probe. Usage: sample_cells.py <probe.exe> <out.vec>"""
import subprocess
import sys

sys.path.insert(0, sys.path[0])
from myref import ref, fmt_hex, encode, _q

W = {"f16": 4, "f32": 8, "f64": 16}


def neg(fmt, x):
    return x ^ _q(fmt)["sign"]


def build():
    cs = []
    for fmt in ("f16", "f32", "f64"):
        q = _q(fmt)
        from myref import FMTS
        p = FMTS[fmt]["p"]
        emax = FMTS[fmt]["emax"]
        emin = FMTS[fmt]["emin"]
        maxfin = encode(fmt, 0, (1 << p) - 1, emax - (p - 1))
        one = encode(fmt, 0, 1 << (p - 1), -(p - 1))
        snan = q["inf"] | 0x01
        qnan = q["inf"] | q["qbit"]
        tiny = encode(fmt, 0, 1, emin - (p - 1))
        for op in ("add", "sub", "mul"):
            C = lambda a, b: cs.append((fmt, op, a, b))
            C(snan, one)
            C(one, snan)
            C(qnan, one)
            if op == "sub":
                C(0, q["sign"])       # +0 - -0 = +0 (kernel-correct)
                C(q["sign"], 0)       # -0 - +0 = -0 (kernel-correct)
            else:
                C(0, 0)
                C(q["sign"], q["sign"])
            C(one, neg(fmt, one) if op == "sub" else one)
            if op != "sub":
                C(maxfin, maxfin)      # overflow above (inf+O+I)
            # NOTE: exact cancellations (add(x,-x), sub(x,x)) are NOT
            # sampled: the kernel signs them -0 (finding F2).
            if op == "mul":
                C(maxfin, neg(fmt, maxfin))  # -inf overflow
            if op == "sub":
                C(maxfin, neg(fmt, maxfin))  # 2*maxfin overflow
            C(0, tiny)
            if op != "mul":
                # P1 tiny-exact residual (flags 00); the mul analogue
                # of this shape is an unrepresentable-residual cell
                C(encode(fmt, 0, (1 << (p - 1)) + 1, emin + 1), tiny)
            # even-candidate tie (both rules agree)
            x = encode(fmt, 0, 1 << (p - 1), 0)
            C(x, encode(fmt, 0, 1, -p))
            if fmt != "f16":
                C(one, encode(fmt, 0, 1 << (p - 1), emin))  # far verbatim
    return cs


def main():
    probe, outp = sys.argv[1], sys.argv[2]
    cs = build()
    inp = "".join("%s %s %0*x %0*x\n" % (f, o, W[f], a, W[f], b)
                  for f, o, a, b in cs)
    p = subprocess.run([probe], input=inp, capture_output=True, text=True)
    got = p.stdout.strip().split("\n")
    assert len(got) == len(cs)
    with open(outp, "w", encoding="utf-8") as f:
        for (fmt, op, a, b), ln in zip(cs, got):
            h, t, fl = ln.split()
            eh, et, ef = ref(fmt, op, a, b)
            assert (h, t, fl) == (fmt_hex(fmt, eh), fmt_hex(fmt, et), "%02x" % ef), \
                (fmt, op, a, b, ln, eh, et, ef)
            w = W[fmt]
            f.write("msf%s_augmented_%s - %0*x %0*x -> %s %s %s exact-py-t2:verifier-sample\n" % (
                fmt[1:], op, w, a, w, b, h, t, fl))
    print("sample_cells: %d kernel-correct cells -> %s" % (len(cs), outp))


if __name__ == "__main__":
    main()
