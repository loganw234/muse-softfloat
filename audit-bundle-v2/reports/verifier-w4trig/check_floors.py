"""Independent check: every committed table entry is the exact 384-bit floor.

Method (own code): parse worktrees/verify4-trig/src/msf_trig_tables.h;
for 1/k! entries compute the exact rational with Python integers
(math.factorial, no floating point anywhere) and take the exact floor
to a normalized 384-bit significand; for pi use mpmath at dps 300/240
(a different precision pair than the generator's 260/210) with a
+-2^-590 bracket-stability check. Report any entry where
stored > true or true >= stored+1ulp.
"""
import math
import re
import sys
from fractions import Fraction

import mpmath

W_TOP = 384
HDR = "worktrees/verify4-trig/src/msf_trig_tables.h"


def floor_entry(v: Fraction):
    assert v > 0
    e = v.numerator.bit_length() - v.denominator.bit_length()
    while Fraction(2) ** e > v:
        e -= 1
    while Fraction(2) ** (e + 1) <= v:
        e += 1
    scaled = v * Fraction(2) ** (W_TOP - 1 - e)
    m = scaled.numerator // scaled.denominator
    assert 2 ** (W_TOP - 1) <= m < 2 ** W_TOP
    return e, m


def parse_header(path):
    text = open(path).read()
    entries = []  # (name, e, m)
    for mobj in re.finditer(
            r"\{\s*(-?\d+),\s*\{([^}]*)\}\s*\},?\s*/\*\s*(.*?)\s*\*/",
            text):
        e = int(mobj.group(1))
        limbs = [int(x, 16) for x in re.findall(r"0x([0-9a-fA-F]+)u",
                                                mobj.group(2))]
        assert len(limbs) == 12, mobj.group(3)
        m = sum(limb << (32 * i) for i, limb in enumerate(limbs))
        entries.append((mobj.group(3), e, m))
    return text, entries


def main():
    text, entries = parse_header(HDR)
    by_name = {}
    for name, e, m in entries:
        by_name.setdefault(name, []).append((e, m))
    assert by_name["pi"] and len(by_name["pi"]) == 1
    nsin = sum(1 for n in by_name if n.endswith("!") and n in
               {f"1/{2*k+1}!" for k in range(60)})
    print(f"parsed entries: {len(entries)} (pi + sin + cos rows)")
    bad = 0
    # exact factorial-reciprocal entries
    for name, e, m in entries:
        mm = re.fullmatch(r"1/(\d+)!", name)
        if not mm:
            continue
        k = int(mm.group(1))
        true = Fraction(1, math.factorial(k))
        te, tm = floor_entry(true)
        lo = Fraction(tm) * Fraction(2) ** (te - (W_TOP - 1))
        hi = Fraction(tm + 1) * Fraction(2) ** (te - (W_TOP - 1))
        if not (te == e and tm == m):
            print(f"MISMATCH {name}: header e={e} regen e={te} "
                  f"m_eq={tm == m}")
            bad += 1
        assert lo <= true < hi  # containment of the true value
    print(f"factorial entries checked exact; mismatches={bad}")
    # pi at an independent precision pair
    outs = []
    for dps in (300, 240):
        mpmath.mp.dps = dps
        p = mpmath.mp.pi
        sign, man, exp, _bc = p._mpf_
        assert sign == 0
        outs.append(Fraction(man) * Fraction(2) ** exp)
    a, b = outs
    import math as _m
    print(f"pi: |dps300-dps240| ~= 2^{_m.log2(float(abs(a-b))):.1f}")
    assert abs(a - b) < Fraction(2) ** -600
    bracket = Fraction(2) ** -590
    e1, m1 = floor_entry(a - bracket)
    e2, m2 = floor_entry(a + bracket)
    assert (e1, m1) == (e2, m2), "pi floor not bracket-stable"
    he, hm = by_name["pi"][0]
    print(f"pi header e={he} indep e={e1} m_eq={hm == m1}")
    if (he, hm) != (e1, m1):
        print("PI MISMATCH")
        bad += 1
    # exponent plausibility of each entry (normalized?)
    for name, e, m in entries:
        if not (2 ** 383 <= m < 2 ** 384):
            print(f"UNNORMALIZED {name}")
            bad += 1
    print(f"total entries={len(entries)} bad={bad}")
    return 1 if bad else 0


sys.exit(main())
