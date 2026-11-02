#!/usr/bin/env python3
"""onecells.py - verifier-w5aug Probe 1: every flag-table cell at all
formats x ops. myref.py decides each case; probe_aug.exe (the copy's
kernel) answers; mismatches are findings. Usage:
  onecells.py <probe.exe> ; exit nonzero on any mismatch."""
import subprocess
import sys

sys.path.insert(0, sys.path[0])
from myref import ref, fmt_hex, decode

FMTS = ("f16", "f32", "f64")
P = {"f16": 11, "f32": 24, "f64": 53}
EMAX = {"f16": 15, "f32": 127, "f64": 1023}
EMIN = {"f16": -14, "f32": -126, "f64": -1022}


def enc(fmt, sign, mag, exp):
    from myref import encode
    b = encode(fmt, sign, mag, exp)
    assert b is not None, (fmt, sign, mag, exp)
    return b


def neg(fmt, x):
    from myref import _q
    return x ^ _q(fmt)["sign"]


def cases():
    out = []  # (label, fmt, op, a, b)
    for fmt in FMTS:
        from myref import _q, default_qnan
        q = _q(fmt)
        p = P[fmt]
        maxfin = enc(fmt, 0, (1 << p) - 1, EMAX[fmt] - (p - 1))
        minnorm = enc(fmt, 0, 1 << (p - 1), EMIN[fmt] - (p - 1))
        minsub = enc(fmt, 0, 1, EMIN[fmt] - (p - 1))
        one = enc(fmt, 0, 1 << (p - 1), -(p - 1))  # 2^0
        half_ulp_one = enc(fmt, 0, 1, -(p - 1) - 1)  # ulp(1)/2
        snan = q["inf"] | 0x01
        qnan = default_qnan(fmt)
        qnan2 = q["inf"] | q["qbit"] | 0x05
        for op in ("add", "sub", "mul"):
            C = lambda a, b, lab: out.append(("%s/%s/%s" % (fmt, op, lab), fmt, op, a, b))
            C(snan, one, "snan-first")
            C(one, snan, "snan-second")
            C(qnan, qnan2, "qnan-only")
            C(qnan, one, "qnan-first")
            C(one, qnan, "qnan-second")
            C(neg(fmt, snan), qnan, "snan+qnans")
            if op == "mul":
                C(0, q["inf"], "invalid-0xinf")
                C(q["inf"], 0, "invalid-infx0")
                C(q["inf"], neg(fmt, q["inf"]), "inf-product")
                C(q["inf"], one, "inf-exact")
                C(minsub, minsub, "tiny-product")
            else:
                C(q["inf"], neg(fmt, q["inf"]) if op == "add" else q["inf"], "invalid-inf-inf")
                C(q["inf"], q["inf"] if op == "add" else neg(fmt, q["inf"]), "inf-exact")
                C(q["inf"], one, "inf-finite")
                C(one, q["inf"], "finite-inf")
            C(0, 0, "zero+zero")
            C(q["sign"], q["sign"], "zero-negneg")
            C(0, q["sign"], "zero-opp")
            C(q["sign"], 0, "zero-opp-rev")
            C(one, neg(fmt, one), "cancel" if op != "mul" else "mul-neg")
            C(maxfin, maxfin if op == "mul" else maxfin, "overflow-finite")
            # RTTZ ties at x's own scale: x + ulp(x)/2 is an exact
            # midpoint; odd x discriminates RTTZ from ties-to-even.
            # e is the top-bit exponent of the x binade (x kept
            # normal: EMIN+1 <= e <= EMAX-1).
            from myref import encode
            es = sorted(e for e in (EMIN[fmt] + 1, EMIN[fmt] + 2, -1, 0, 1,
                                    7, EMAX[fmt] - 2, EMAX[fmt] - 1)
                        if EMIN[fmt] + 1 <= e <= EMAX[fmt] - 1)
            for e in es:
                h = encode(fmt, 0, 1, e - p)  # ulp(x)/2 at this binade
                if h is None:
                    continue
                for s in ((1 << (p - 1)), (1 << (p - 1)) + 1, (1 << p) - 2):
                    x = encode(fmt, 0, s, e - (p - 1))
                    if x is None:
                        continue
                    C(x, h, "tie-e%d-s%d" % (e, s))
                    C(neg(fmt, x), h, "tie-neg-e%d-s%d" % (e, s))
                    C(x, neg(fmt, h), "subtie-e%d-s%d" % (e, s))
            # binade-crossing tie: x a power of two, step below is half;
            # x - ulp(x)/4 is the midpoint between x and x-ulp(x)/2.
            for e in es:
                if e <= EMIN[fmt] + 1:
                    continue
                x = encode(fmt, 0, 1 << (p - 1), e)
                qtr = encode(fmt, 0, 1, e - p - 1)
                if x is None or qtr is None:
                    continue
                C(x, neg(fmt, qtr), "subtie-xbin-e%d" % e)
                C(neg(fmt, x), qtr, "tie-xbin-neg-e%d" % e)
            # mul ties: (2^(p-1)+2^s)(2^(p-1)+2^t), s+t = p-2 leaves
            # exactly the half bit in the dropped half of the product.
            if op == "mul":
                for s in range(0, p - 1):
                    t = (p - 2) - s
                    a = enc(fmt, 0, (1 << (p - 1)) + (1 << s), -(p - 1))
                    b = enc(fmt, 0, (1 << (p - 1)) + (1 << t), -(p - 1))
                    C(a, b, "multie-s%d-t%d" % (s, t))
            # overflow-threshold tie: maxfin + half-ulp(maxfin) is exactly
            # the threshold -> max-finite head, half-ulp tail.
            thr_half = enc(fmt, 0, 1, EMAX[fmt] - (p - 1) - 1)
            C(maxfin, thr_half, "ovf-threshold-tie")
            C(maxfin, enc(fmt, 0, 3, EMAX[fmt] - (p - 1) - 2), "ovf-one-above")
            C(maxfin, enc(fmt, 0, 1, EMAX[fmt] - (p - 1) - 2), "ovf-quarter")
            # verbatim far-operand pair (f32/f64 only; f16 span <= 40)
            if fmt != "f16":
                tiny = enc(fmt, 0, 1 << (p - 1), EMIN[fmt])
                C(one, tiny, "far-verbatim")
                C(tiny, one, "far-verbatim-rev")
                C(neg(fmt, one), tiny, "far-verbatim-neg")
            # P1 tiny-exact residual: head normal, residual tiny exact.
            C(enc(fmt, 0, (1 << (p - 1)) + 1, EMIN[fmt] + 1),
              enc(fmt, 0, 1, EMIN[fmt] - (p - 1)), "p1-tiny-exact")
            # exact powers / exact cells
            C(one, one, "one-one")
            C(minnorm, minnorm, "minnorm-minnorm")
            C(minsub, minsub if op == "mul" else 0, "minsub-cell")
    return out


def main():
    probe = sys.argv[1]
    cs = cases()
    inp = "".join("%s %s %s %s\n" % (f, o, fmt_hex(f, a), fmt_hex(f, b))
                  for _, f, o, a, b in cs)
    p = subprocess.run([probe], input=inp, capture_output=True, text=True)
    lines = p.stdout.strip().split("\n")
    assert len(lines) == len(cs), (len(lines), len(cs))
    bad = 0
    for (lab, fmt, op, a, b), ln in zip(cs, lines):
        gh, gt, gf = ln.split()
        eh, et, ef = ref(fmt, op, a, b)
        got = (gh, gt, gf)
        want = (fmt_hex(fmt, eh), fmt_hex(fmt, et), "%02x" % ef)
        flag = "ok" if got == want else "MISMATCH"
        if got != want:
            bad += 1
            print("%s %s %s %s: got %s %s/%s want %s %s/%s" % (
                flag, lab, fmt_hex(fmt, a), fmt_hex(fmt, b),
                gh, gt, gf, want[0], want[1], want[2]))
    print("onecells: %d cases, %d mismatches" % (len(cs), bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
