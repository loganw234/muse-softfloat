#!/usr/bin/env python3
"""Empirical check of the jam-equivalence claim for the planned
hypot kernel (121-bit anchored window, floor+sticky vs shr_jam
alignment + parity jam + rem-only sticky), plus sanity of the
floor sim against proto_alg.hypot_exact_decision.

Also checks the dropped-sticky variant (floor alignment,
sticky = rem only) DOES diverge, and exhibits witnesses.
Finite nonzero pairs only (specials are order code, not kernel).
"""
import random
import sys
sys.path.insert(0, r"C:\Users\logan\source\repos\Muse-Softfloat\scratch\sf2-algebraic")
from math import isqrt
from proto_alg import round_pack, decode, hypot_exact_decision, FMT

RMS = ("te", "tz", "tp", "tn")

def sim(fmt, abits, bbits, variant):
    """variant: floor | jam | nosticky. Returns packed list or None(Both zero)."""
    _, _, asig, aexp = decode(fmt, abits)
    _, _, bsig, bexp = decode(fmt, bbits)
    # order by magnitude: compare (exp+bitlen, aligned)
    def top(s, e):
        return e + s.bit_length() if s else -10**9
    ta, tb = top(asig, aexp), top(bsig, bexp)
    swap = ta < tb or (ta == tb and (asig << max(0, aexp - bexp)) < (bsig << max(0, bexp - aexp)))
    if swap:
        asig, aexp, bsig, bexp = bsig, bexp, asig, aexp
    if asig == 0:
        return None
    sa, sb = asig * asig, bsig * bsig
    lsh = 121 - sa.bit_length()
    a_win = sa << lsh
    net = lsh - 2 * (aexp - bexp)
    jam = variant == "jam"
    if net >= 0:
        b_win, tail = sb << net, False
    else:
        k = -net
        dropped = sb & ((1 << k) - 1) if k < 512 else sb
        if jam:
            b_win, tail = (sb >> k) | (1 if dropped else 0), False
        else:
            b_win, tail = sb >> k, dropped != 0
    tot = a_win + b_win
    ew = 2 * aexp - lsh
    pdrop = False
    if ew & 1:
        if jam:
            R = (tot >> 1) | (tot & 1)
        else:
            R, pdrop = tot >> 1, bool(tot & 1)
        ew += 1
    else:
        R = tot
    Q = isqrt(R)
    rem = R - Q * Q
    if variant == "floor":
        sticky = tail or pdrop or rem != 0
    else:
        sticky = rem != 0
    return [round_pack(fmt, 0, Q, ew // 2, sticky, rm) for rm in RMS]

def rand_finite(rng, fmt):
    F = FMT[fmt]
    while True:
        x = rng.getrandbits(F["bits"] - 1)  # positive
        cls, *_ = decode(fmt, x)
        if cls in ("sub", "norm"):
            return x

def main():
    rng = random.Random(20261028)
    total = {"jam": 0, "nosticky": 0}
    checked = 0
    sanity_bad = 0
    nosticky_examples = []
    for fmt, n in (("f16", 60000), ("f32", 120000), ("f64", 120000)):
        for i in range(n):
            a, b = rand_finite(rng, fmt), rand_finite(rng, fmt)
            pf = sim(fmt, a, b, "floor")
            if i % 977 == 0:  # exact-decider sanity on a stride sample
                ex = [hypot_exact_decision(fmt, a, b, rm) for rm in RMS]
                if ex != pf:
                    sanity_bad += 1
                    print(f"SANITY-DISAGREE {fmt} {a:x} {b:x} floor={pf} exact={ex}")
            if sim(fmt, a, b, "jam") != pf:
                total["jam"] += 1
                if total["jam"] <= 5:
                    print(f"JAM-DIVERGE {fmt} {a:x} {b:x}")
            if sim(fmt, a, b, "nosticky") != pf:
                total["nosticky"] += 1
                if len(nosticky_examples) < 6:
                    nosticky_examples.append((fmt, a, b))
            checked += 1
    # structured tiny-b: b at min subnormal .. few, a = 1.0 and binade edges
    for fmt in ("f32", "f64"):
        F = FMT[fmt]
        one = F["bias"] << F["frac"]
        for a in (one, one + 1, (1 << F["frac"]), ((F["bias"] + 40) << F["frac"])):
            for b in (1, 2, 3, 7, 1 << (F["frac"] - 1)):
                pf = sim(fmt, a, b, "floor")
                if sim(fmt, a, b, "jam") != pf:
                    total["jam"] += 1
                    print(f"JAM-DIVERGE-TINY {fmt} {a:x} {b:x}")
                if sim(fmt, a, b, "nosticky") != pf:
                    total["nosticky"] += 1
                    nosticky_examples.append((fmt, a, b))
                checked += 1
    print(f"checked={checked} jam_divergences={total['jam']} "
          f"nosticky_divergences={total['nosticky']} sanity_bad={sanity_bad}")
    for fmt, a, b in nosticky_examples[:6]:
        print(f"NOSTICKY-WITNESS {fmt} {a:x} {b:x} floor={sim(fmt, a, b, 'floor')} "
              f"nosticky={sim(fmt, a, b, 'nosticky')}")

if __name__ == "__main__":
    main()
