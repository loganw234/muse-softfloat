#!/usr/bin/env python3
"""bsearch.py - verifier-w5aug WIDTHS probe: binade-boundary and
verbatim-gap counterexample search at f32/f64 (kernel vs myref).
Any kernel/myref diff NOT shaped like the three known defects
(F1 tie-TE, F2 zero-sign, F3 mul-underflow) is a NEW finding.
Usage: bsearch.py <probe.exe>"""
import subprocess
import sys

sys.path.insert(0, sys.path[0])
from myref import ref, decode, _q, FMTS

OPS = ("add", "sub", "mul")


def enc_try(fmt, sign, mag, exp):
    from myref import encode
    return encode(fmt, sign, mag, exp)


def neighbours(fmt, bits):
    """Representable neighbours of a finite encoding + itself."""
    q = _q(fmt)
    cls, s, m, e = decode(fmt, bits)
    assert cls in ("zero", "finite")
    mag = bits & ~q["sign"]
    out = [bits]
    if mag > 0:
        out.append((bits & q["sign"]) | (mag - 1))
    # +1 unless inf
    if mag + 1 < q["inf"]:
        out.append((bits & q["sign"]) | (mag + 1))
    return sorted(set(out))


def centers(fmt):
    from myref import encode
    P = FMTS[fmt]["p"]
    EMAX = FMTS[fmt]["emax"]
    EMIN = FMTS[fmt]["emin"]
    cs = []
    for e in (EMIN, EMIN + 1, EMIN + 2, -1, 0, 1, 2, EMAX - 2, EMAX - 1, EMAX):
        for m in (0, 1, 2, (1 << (P - 1)) - 1, 1 << (P - 1),
                  (1 << (P - 1)) + 1, (1 << P) - 2, (1 << P) - 1):
            if m == 0:
                b = encode(fmt, 0, 0, 0)
            else:
                # place significand m with top bit at e
                b = encode(fmt, 0, m, e - (m.bit_length() - 1))
            if b is not None:
                cs.append(b)
    # extremes
    q = _q(fmt)
    cs += [0, q["sign"], 1, q["sign"] | 1, q["inf"] - 1,
           (q["sign"] | q["inf"]) - 1]
    return sorted(set(cs))


def is_adjacent(fmt, x, y):
    q = _q(fmt)
    return abs((x & ~q["sign"]) - (y & ~q["sign"])) == 1 and \
        (x & q["sign"]) == (y & q["sign"])


def explained(fmt, op, a, b, gh, gt, gf, wh, wt, wf):
    """True if the got/want deviation matches F1, F2 or F3 only."""
    q = _q(fmt)
    # F3: bits identical, want adds underflow to got (mul only)
    if (gh, gt) == (wh, wt) and op == "mul" and (gf | 0x08) == wf and gf != wf:
        return "F3-mul-underflow"
    # F2: zero pair sign flip only
    if gh == gt and wh == wt and (gh ^ wh) == q["sign"] and \
            (gh & ~q["sign"]) == 0 and (wh & ~q["sign"]) == 0 and gf == wf == 0:
        return "F2-zero-sign"
    # F1: heads adjacent, flags equal (finite ties); ovf tie HTF
    if gf == wf and gh != wh and is_adjacent(fmt, gh, wh):
        return "F1-tie"
    if op in ("add", "sub") and {gf, wf} == {0x00, 0x14} and \
            ((gh & ~q["sign"]) == q["inf"]) != ((wh & ~q["sign"]) == q["inf"]):
        return "F1-ovf-tie"
    return None


def main():
    probe = sys.argv[1]
    cases = []
    for fmt in ("f32", "f64"):
        q = _q(fmt)
        for c in centers(fmt):
            pool = neighbours(fmt, c)
            pool2 = sorted(set(pool + [x ^ q["sign"] for x in pool]))
            for a in pool2:
                for b in pool2:
                    for op in OPS:
                        cases.append((fmt, op, a, b))
        # verbatim far pairs: huge x tiny (both orders, signs)
        q = _q(fmt)
        P = FMTS[fmt]["p"]
        tiny = enc_try(fmt, 0, 1, FMTS[fmt]["emin"] - (P - 1))
        huge = enc_try(fmt, 0, (1 << P) - 1, FMTS[fmt]["emax"] - (P - 1))
        for s in (0, 1):
            for op in OPS:
                cases.append((fmt, op, huge | (s * q["sign"]), tiny))
                cases.append((fmt, op, tiny, huge | (s * q["sign"])))
    W = {"f16": 4, "f32": 8, "f64": 16}
    inp = "".join("%s %s %0*x %0*x\n" % (f, o, W[f], a, W[f], b)
                  for f, o, a, b in cases)
    p = subprocess.run([probe], input=inp, capture_output=True, text=True)
    lines = p.stdout.strip().split("\n")
    assert len(lines) == len(cases), (len(lines), len(cases))
    from collections import Counter
    shapes = Counter()
    new = []
    for (fmt, op, a, b), ln in zip(cases, lines):
        gh, gt, gf = ln.split()
        eh, et, ef = ref(fmt, op, a, b)
        w = W[fmt]
        want = ("%0*x" % (w, eh), "%0*x" % (w, et), "%02x" % ef)
        if (gh, gt, gf) != want:
            ex = explained(fmt, op, a, b, int(gh, 16), int(gt, 16),
                           int(gf, 16), eh, et, ef)
            if ex is None:
                new.append((fmt, op, a, b, gh, gt, gf, want))
                if len(new) <= 15:
                    print("NEW-FINDING %s %s %0*x %0*x: got %s %s/%s want %s %s/%s" % (
                        fmt, op, w, a, w, b, gh, gt, gf, want[0], want[1], want[2]))
            else:
                shapes[ex] += 1
    print("bsearch: %d cases, %d explained, %d NEW" %
          (len(cases), sum(shapes.values()), len(new)))
    for k in sorted(shapes):
        print(" ", k, shapes[k])
    return 1 if new else 0


if __name__ == "__main__":
    sys.exit(main())
