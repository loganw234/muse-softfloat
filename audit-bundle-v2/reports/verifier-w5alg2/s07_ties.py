#!/usr/bin/env python3
"""s07_ties.py - tie families: replay, te vs ta census, subnormal census.

Sources: the study's two measured binary16 ties, the parcel-cited
062c/067b pair, and my OWN Euclid-triple tie construction per format
(odd (p+1)-bit hypotenuse, legs with <= p-bit odd parts, at several
exponents). For each pair: my decide (tie? te!=ta? ta==away?), the
kernel floor build, and the committed-vector expectation if present.
Plus: subnormal-output census over the committed hypot lines.
"""
import random
import subprocess
import sys
import os
from fractions import Fraction

sys.path.insert(0, "scratch/verifier-w5alg2")
from mydecide import FMTS, decide, encode_value, specials  # noqa: E402

OUT = "scratch/verifier-w5alg2/out"
EXE = OUT + "/harness_floor.exe"
RMS = ("te", "tz", "tp", "tn", "ta")


def kernel(pairs):
    blob = "".join(f"{fi} {a:x} {b:x}\n" for fi, a, b in pairs)
    kh = subprocess.run([EXE, "hypot"], input=blob, capture_output=True,
                        text=True)
    if kh.returncode != 0:
        raise RuntimeError(kh.stderr[-2000:])
    out = []
    for line in kh.stdout.splitlines():
        t = line.split()
        out.append([(int(t[2 * i], 16), int(t[2 * i + 1], 16))
                    for i in range(5)])
    return out


def is_tie(fi, a, b):
    if specials(fi, a, b) is not None:
        return False
    e = decide(fi, a, b)
    return e[0] != e[4]


def euclid_ties(fi, count, seed):
    """My own tie construction: Euclid triples, odd (p+1)-bit hyp."""
    f = FMTS[fi]
    p = f["p"]
    rng = random.Random(seed)
    out = []
    tries = 0
    while len(out) < count and tries < 500000:
        tries += 1
        u = rng.randrange(2, 1 << ((p + 3) // 2 + 2))
        v = rng.randrange(1, u)
        if (u - v) % 2 == 0:
            continue
        hyp = u * u + v * v
        if hyp.bit_length() != p + 1 or hyp % 2 == 0:
            continue
        l1, l2 = u * u - v * v, 2 * u * v

        def odd_bl(x):
            while x % 2 == 0 and x:
                x //= 2
            return x.bit_length()
        if odd_bl(l1) > p or odd_bl(l2) > p:
            continue
        for te_ in (f["emin"] + 2, -4, 0, 8):
            if not (f["emin"] <= te_ <= f["emax"]):
                continue
            k = te_ - (hyp.bit_length() - 1)
            try:
                a = encode_value(fi, Fraction(l1) * Fraction(2) ** k)
                b = encode_value(fi, Fraction(l2) * Fraction(2) ** k)
            except AssertionError:
                continue
            if is_tie(fi, a, b):
                out.append((a, b))
                break
    return out


def main():
    f16 = FMTS[0]
    pairs = []
    labels = []
    # study tie 1 (Sec. 6): 395*2^-22, 1659*2^-24 at f16
    a = encode_value(0, Fraction(395) * Fraction(2) ** -22)
    b = encode_value(0, Fraction(1659) * Fraction(2) ** -24)
    pairs += [(0, a, b), (0, b, a)]
    labels += ["study-tie-1", "study-tie-1-swapped"]
    # parcel-cited pair
    pairs += [(0, 0x062c, 0x067b), (0, 0x067b, 0x062c)]
    labels += ["parcel-062c", "parcel-062c-swapped"]
    for fi in (0, 1, 2):
        for a, b in euclid_ties(fi, 6, 9000 + fi):
            pairs.append((fi, a, b))
            labels.append(f"euclid-f{FMTS[fi]['w']}")
    mine = [decide(fi, a, b) for fi, a, b in pairs]
    kern = kernel(pairs)
    n_tie = sum(1 for e in mine if e[0] != e[4])
    print(f"TIES: pairs={len(pairs)} exact-ties-per-mydec={n_tie}")
    mm = 0
    for (fi, a, b), lab, e, k in zip(pairs, labels, mine, kern):
        tie = "TIE" if e[0] != e[4] else "non-tie"
        ok = "OK " if list(e) == list(k) else "BAD"
        if list(e) != list(k):
            mm += 1
        print(f"  [{lab}] fi={fi} a={a:x} b={b:x} {tie} kernel:{ok} "
              f"te={e[0][0]:x}/{e[0][1]:02x} ta={e[4][0]:x}/{e[4][1]:02x} "
              f"k_te={k[0][0]:x}/{k[0][1]:02x} k_ta={k[4][0]:x}/{k[4][1]:02x}")
    # te-vs-ta census over the committed ties-tagged lines
    te_ne_ta = tie_lines = 0
    sub_out = 0
    for fn, fi in (("alg-f16.vec", 0), ("alg-f32.vec", 1), ("alg-f64.vec", 2)):
        with open(f"worktrees/verify5-alg2/tests/vectors/{fn}") as fh:
            for line in fh:
                t = line.split()
                if len(t) < 8 or "hypot" not in t[0]:
                    continue
                rm, rb, rf = t[1], int(t[5], 16), int(t[6], 16)
                tag = t[7] if len(t) > 7 else ""
                if "ties" in tag:
                    tie_lines += 1
                f = FMTS[fi]
                ew = f["w"] - 1 - f["t"]
                ef = (rb >> f["t"]) & ((1 << ew) - 1)
                if ef == 0 and rb & ((1 << f["t"]) - 1):
                    sub_out += 1
    print(f"COMMITTED: ties-tagged hypot lines={tie_lines} "
          f"subnormal-output hypot lines={sub_out}")
    print("TIES", "PASS" if mm == 0 else "FAIL")
    return 0 if mm == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
